{
    'name': 'Reporte de Anticuamiento de Stock',
    'version': '17.0.1.0.0',
    'author': 'Dany Chavez',
    'category': 'Extra Tools',
    'depends': [
        'base',
        'report_xlsx',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/report_stock_aging_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
