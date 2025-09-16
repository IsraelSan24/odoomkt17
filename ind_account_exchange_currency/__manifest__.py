{
    'name': 'Indomin - Tipo de Cambio Contabilidad',
    'version': '17.0.1.0.0',
    'author': 'Dany Chavez',
    'category': 'Accounting/Accounting',
    'description': 'Este módulo permite almacenar el valor del tipo de cambio en la factura que se actualiza según la fecha y la moneda',
    'summary': """
        Este tipo de cambio es el mismo que Odoo utiliza para convertir valores a la moneda de la empresa, pero lo mostramos en la factura y lo almacenamos, lo que permite recuperarlo fácilmente en un informe
    """,
    'depends': [
        'account',
    ],
    'data': [
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
