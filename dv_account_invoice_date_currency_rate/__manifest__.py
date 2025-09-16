{
    'name': """
        Account Invoice Date's Currency Rate. |
        Tipo de cambio a la fecha de emisión de la Factura
    """,

    'summary': """
        Converts the invoice currency to the currency rate of the invoice date |
        Conversión a Tipo de cambio a la fecha de emisión de la factura.
    """,

    'description': """
        Converts the invoice currency to the currency rate of the invoice date. |
        Conversión a Tipo de cambio a la fecha de emisión de la factura.
    """,

	'author': 'Develogers',
    'website': 'https://develogers.com',
    'support': 'especialistas@develogers.com',
    'live_test_url': 'https://demoperu.develogers.com',
    'license': 'LGPL-3',

    'category': 'Localization',
    'version': '17.0',
    
    'price': 39.99,
    'currency': 'EUR',

    'depends': [
        'account',
    ],

    'data': [
        'views/account_move_views.xml',
    ],

    'images': ['static/description/banner.gif'],

    'installable': True,
    'application': True,
    'auto_install': False,
}
