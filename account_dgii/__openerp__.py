# -*- coding: utf-8 -*-

{
    'name' : 'Account DGII',
    'version' : '1.1',
    'summary': '',
    'sequence': 30,
    'description': """
    
    Modulo para el manejo de los NCF y los reportes de la DGII.

    """,
    'author': 'sisne, srl',
    'category': 'Account',
    'website': 'http://sisne.do/',
    'depends' : ['purchase','account'],
    'data': [
        'views/account_invoice_view.xml',
        'views/partner_view.xml',
        'views/service_tax_view.xml',
        'wizard/report_wizard.xml',
        'demo/purchase_good_category.xml',
        'views/account_dgii_menuitem.xml',
    ],
    # 'demo': [
    #         'demo/purchase_good_category.xml',
    #         ],
    'installable': True,
    'auto_install': False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: