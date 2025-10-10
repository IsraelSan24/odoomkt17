{
    'name': 'Indomin - Factura en movimientos de Stock',
    'author': 'Dany Chavez',
    'version': '17.0.1.0.0',
    'summary': 'Cambios aplicados para el módulo Stock Move Invoice',
    'category': 'Purchase Management',
    'depends': [
        'purchase',
        'stock_move_invoice',
    ],
    'data': [
        'views/stock_picking_views.xml',
        'views/account_move_views.xml',
        'views/purchase_order_views.xml',
        'views/account_move_line_views.xml',
        'views/stock_move_views.xml',
        'views/account_journal.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
