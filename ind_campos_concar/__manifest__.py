{
    'name': 'Indomin - Campos adicionales compatible con CONCAR',
    'version': '17.0.1.0.0',
    'author': 'Juan Carlos León Huayta',
    'maintainer': 'Dany Chavez',
    'category': 'Extra tools',
    'depends': [
        'base',
        'account'
    ],
    'data': [
        'views/account_move_views.xml',
        'views/account_payment_views.xml',
        'views/account_move_line_views.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
