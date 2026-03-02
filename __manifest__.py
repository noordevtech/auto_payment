# -*- coding: utf-8 -*-
{
    'name': 'Auto Payment',
    'version': '19.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Automatically pay invoices for selected clients on a monthly schedule',
    'description': """
Auto Payment
============
This module allows you to configure automatic payment of invoices for specific
clients on a specific day of each month.

Features:
- Configure per-client auto payment rules
- Set the day of month for payment processing
- Choose payment journal and method
- Daily cron job checks and processes payments automatically
- Logs all payment activity for audit trail
    """,
    'author': 'Custom',
    'website': '',
    'license': 'LGPL-3',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/auto_payment_config_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
