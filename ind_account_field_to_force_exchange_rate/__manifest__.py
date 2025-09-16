{
    'name': 'Indomin - Account field to Force Exchange Rate',
    'version': '17.0.1.0.0',
    'author': 'Dany Chavez',
    'category': 'Accounting/Accounting',
    'summary': 'Este módulo creará un campo para forzar el tipo de cambio',
    'description': """
El campo Fuerza de tipo de cambio cambiará el tipo de cambio a uno personalizado en pagos y facturas.
""",
    'depends': [
        'ind_account_exchange_currency',
    ],
    'data': [
        'views/account_move_views.xml',
        'views/account_payment_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
