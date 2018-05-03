# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Account 606 Report',
    'version': '1.0',
    'category': 'Accounting',
    'description': """
    """,
    'depends': ['account', 'base_vat_do'],
    'website': 'https://www.odoo.com/page/accounting',
    'data': [
        'views/account_invoice.xml',
        'views/account_tax.xml',
        'wizard/report_wizard.xml',
        'views/menuitem_view.xml',
    ],
}
