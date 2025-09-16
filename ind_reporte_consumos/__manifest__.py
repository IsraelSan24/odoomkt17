{
    'name': 'Indomin Reporte Consumos',
    'author': 'Israel',
    'maintainer': 'Dany Chavez',
    'version': '17.0.1.0.0',
    'description': 'Reporte de consumos a nivel del almacen',
    'depends': [
        "base",
        "stock",
        "purchase_request",
        "account",
        "product",
    ],
    'data':[
        "security/access_groups.xml",  # Archivo que define el grupo
        "security/ir.model.access.csv",  # Archivo que define los permisos
        "wizards/ind_consumption_analysis_views.xml"
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

