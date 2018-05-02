# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Account extended',
    'version': '1.0',
    'category': 'Accounting',
    'description': """
    """,
    'depends': ['account', 'account_dgii'],
    'website': 'https://www.odoo.com/page/accounting',
    'data': [
        'views/account_invoice.xml',
        'views/account_tax.xml',
        'wizard/report_wizard.xml',
        'views/menuitem_view.xml',
    ],
}
