# -*- coding: utf-8 -*-
{
    'name': 'Indomin - Producto Padre',
    'version': '17.0.1.0.0',
    'author': 'Juan Carlos León Huayta',
    'maintainer': 'Dany Chavez',
    'category': 'Extra Tools',
    'sequence': 10,
    'summary': 'Personalizaciones al módulo producto',
    'description': "",
    'depends': [
        'report_xlsx',
        'product',
        'stock',
        'purchase_request'
    ],
    'data': [
        'views/producto_padre_views.xml',
        'views/product_product_views.xml',
        'views/producto_padre_menus.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'reports/ir_actions_report.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
