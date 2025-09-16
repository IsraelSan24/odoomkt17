# -*- coding: utf-8 -*-
{
    'name': 'Indomin - Producto',
    'version': '17.0.1.0.0', #"15.0.2"
    'author': 'Dany Chavez',
    'category': 'Extra Tools',
    'sequence': 10,
    'summary': 'Personalizaciones al módulo producto',
    'description': "",
    'depends': [
        'product',
        'purchase_request'
    ],
    'data': [
        'security/res_groups.xml',
        'views/purchase_order_views.xml',
        'views/purchase_request_views.xml',
        'views/product_category_views.xml',
        'views/product_template_views.xml',
        'views/product_product_views.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
