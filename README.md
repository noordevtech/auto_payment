# Auto Payment - Odoo 19 Addon

Automatically pay invoices for selected clients on a configurable monthly schedule.

## Features

- **Per-Client Configuration** - Set up individual auto-payment rules for each client
- **Monthly Scheduling** - Choose the day of the month (1-28) for automatic payment processing
- **Flexible Payment Options** - Select the payment journal and method per configuration
- **Daily Cron Job** - Processes payments automatically on the configured day
- **Audit Logging** - All payment activity is logged for transparency and troubleshooting

## Installation

1. Copy the `auto_payment` folder into your Odoo addons directory
2. Restart the Odoo server
3. Go to **Apps** > **Update Apps List**
4. Search for **Auto Payment** and click **Install**

## Configuration

1. Navigate to **Invoicing** > **Configuration** > **Auto Payments**
2. Click **Create** to add a new auto-payment rule
3. Fill in the required fields:
 - **Client** - The customer whose invoices will be automatically paid
 - **Payment Day** - Day of the month to process payments (1-28)
 - **Payment Journal** - Bank or cash journal to use
 - **Payment Method** *(optional)* - Specific payment method; defaults to the journal's default

## How It Works

A scheduled action (cron job) runs daily and checks if today matches any configured payment day. When it does, it:

1. Finds all open or partially paid posted invoices for the configured client
2. Registers a payment for each invoice using the `account.payment.register` wizard
3. Logs the result of each payment attempt

## Module Structure

`
auto_payment/
+-- __init__.py
+-- __manifest__.py
+-- data/
| +-- cron.xml
+-- models/
| +-- __init__.py
| +-- auto_payment_config.py
+-- security/
| +-- ir.model.access.csv
+-- views/
 +-- auto_payment_config_views.xml
`

## Dependencies

- **account** (Odoo Invoicing module)

## Access Rights

| Role | Read | Write | Create | Delete |
|-------------------|------|-------|--------|--------|
| Account Manager | Yes | Yes | Yes | Yes |
| Account Invoice | Yes | No | No | No |

## License

LGPL-3
