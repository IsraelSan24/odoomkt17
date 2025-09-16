{
    'name': """
        Target Entries for Invoices and Accounting Entries| 
        Asientos de Destino para Facturas y Asientos Contables
    """,

    'summary': """
        Generates of target entries or entries by nature automatically. |
        Genera asientos de destino o asientos por naturaleza automáticamente.
    """,

    'description': """
        Set up destination accounts from the chart of accounts and generate destination entries automatically. |
        Configura cuentas de destino desde el plan contable y genera asientos de destino automáticamente.
    """,

	'author': 'Develogers',
    'website': 'https://develogers.com',
    'support': 'especialistas@develogers.com',
    'live_test_url': 'https://demo.develogers.com',
    'license': 'LGPL-3',
    'maintainer': 'Dany Chavez',
    'category': 'Accounting',
    'version': '17.0.1.0.0',
    'price': 49.99,
    'currency': 'EUR',
    'depends': [
        'base',
        'account',
        'ind_account'
    ],
    'data': [
        'views/account_move_views.xml',
        'views/account_analytic_account_views.xml',
        'views/account_account_views.xml',
    ],

    'images': ['static/description/banner.gif'],

    'installable': True,
    'application': False,
    'auto_install': False,
}
