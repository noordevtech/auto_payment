# -*- coding: utf-8 -*-
import logging
from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AutoPaymentConfig(models.Model):
    _name = 'auto.payment.config'
    _description = 'Auto Payment Configuration'
    _rec_name = 'display_name'

    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        required=True,
        domain=[('customer_rank', '>', 0)],
        help='The client whose invoices will be automatically paid.',
    )
    payment_day = fields.Integer(
        string='Payment Day',
        required=True,
        default=1,
        help='Day of the month (1-28) when invoices for this client will be automatically paid.',
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Payment Journal',
        required=True,
        domain=[('type', 'in', ('bank', 'cash'))],
        help='The journal to use for automatic payments.',
    )
    payment_method_line_id = fields.Many2one(
        'account.payment.method.line',
        string='Payment Method',
        help='The payment method to use. If left empty, the default method of the journal will be used.',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )

    @api.constrains('payment_day')
    def _check_payment_day(self):
        for record in self:
            if record.payment_day < 1 or record.payment_day > 28:
                raise UserError(_('Payment day must be between 1 and 28.'))

    @api.depends('partner_id', 'payment_day')
    def _compute_display_name(self):
        for record in self:
            if record.partner_id:
                record.display_name = _('%(partner)s - Day %(day)s',
                                        partner=record.partner_id.name,
                                        day=record.payment_day)
            else:
                record.display_name = _('New')

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        """Reset payment method when journal changes."""
        self.payment_method_line_id = False

    def _get_open_invoices(self):
        """Find all open/partially paid posted customer invoices for this config's partner."""
        self.ensure_one()
        return self.env['account.move'].search([
            ('partner_id', '=', self.partner_id.id),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ('not_paid', 'partial')),
            ('company_id', '=', self.company_id.id),
        ])

    def _pay_invoices(self, invoices):
        """Register payment for the given invoices using account.payment.register wizard."""
        self.ensure_one()
        if not invoices:
            return self.env['account.payment']

        all_payments = self.env['account.payment']

        for invoice in invoices:
            try:
                # Get the payable/receivable lines from the invoice
                line_ids = invoice.line_ids.filtered(
                    lambda l: l.account_type in ('asset_receivable', 'liability_payable')
                    and not l.reconciled
                )
                if not line_ids:
                    _logger.info(
                        'Auto Payment: No receivable lines found for invoice %s',
                        invoice.name,
                    )
                    continue

                # Create the payment register wizard
                ctx = {
                    'active_model': 'account.move',
                    'active_ids': invoice.ids,
                }
                wizard_vals = {
                    'journal_id': self.journal_id.id,
                    'payment_date': fields.Date.context_today(self),
                }
                if self.payment_method_line_id:
                    wizard_vals['payment_method_line_id'] = self.payment_method_line_id.id

                wizard = self.env['account.payment.register'].with_context(**ctx).create(wizard_vals)
                payments = wizard._create_payments()
                all_payments |= payments

                _logger.info(
                    'Auto Payment: Successfully paid invoice %s for partner %s (amount: %s %s)',
                    invoice.name,
                    self.partner_id.name,
                    invoice.amount_total,
                    invoice.currency_id.name,
                )
            except Exception as e:
                _logger.error(
                    'Auto Payment: Failed to pay invoice %s for partner %s: %s',
                    invoice.name,
                    self.partner_id.name,
                    str(e),
                )

        return all_payments

    @api.model
    def _cron_auto_pay_invoices(self):
        """Cron method: find configs matching today's day and process payments."""
        today = fields.Date.context_today(self)
        current_day = today.day

        _logger.info('Auto Payment: Running cron job for day %s', current_day)

        configs = self.search([
            ('payment_day', '=', current_day),
            ('active', '=', True),
        ])

        if not configs:
            _logger.info('Auto Payment: No configurations found for day %s', current_day)
            return

        for config in configs:
            _logger.info(
                'Auto Payment: Processing config for partner %s',
                config.partner_id.name,
            )
            invoices = config._get_open_invoices()
            if invoices:
                _logger.info(
                    'Auto Payment: Found %d open invoice(s) for %s',
                    len(invoices),
                    config.partner_id.name,
                )
                config._pay_invoices(invoices)
            else:
                _logger.info(
                    'Auto Payment: No open invoices found for %s',
                    config.partner_id.name,
                )

        _logger.info('Auto Payment: Cron job completed')
