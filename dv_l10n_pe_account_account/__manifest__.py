{
    'name': """
        Localización Peruana en Facturación
    """,

    'summary': """
        Permite registrar facturas de proveedores con campos personalizados para la contabilidad peruana.
    """,

    'description': """
        Agrega campos en facturas de proveedores.
    """,

    'author': 'Develogers',
    'website': 'https://www.linkedin.com/in/ailton-salguero',
    'support': 'especialistas@develogers.com',
    'live_test_url': 'https://wa.me/message/NN37LBBZC5TQA1',
    'license': 'Other proprietary',

    'category': 'Localization',
    'version': '17.0',
    
    'price': 79.99,
    'currency': 'EUR',

    'depends': [
        'l10n_latam_invoice_document',
        'l10n_pe',
        'dv_l10n_pe_edi_table',
        'dv_account_invoice_date_currency_rate',
    ],

    'data': [
        'views/account_account_views.xml',
        'views/account_move_views.xml',
        'views/account_move_line_views.xml',
        'views/l10n_latam_identification_type_views.xml',
        'views/product_template_views.xml',
        'views/menu_item_views.xml',
        'data/res.partner.csv',
        'data/l10n_latam.document.type.csv',
        #'data/account_tax_data.xml',
    ],
    
    'images': ['static/description/banner.gif'],
    
    'auto_install': False,
	'application': True,
	'installable': True,
}
