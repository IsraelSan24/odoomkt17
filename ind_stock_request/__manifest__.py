{
    "name": 'Stock Request',
    "author": 'Javier Yataco',
    'version': '17.0.1.0.0',
    'maintainer': 'Ronaldo Lopez',
    "summary": """
    The funcionality of this module is to have a requirement to picking products from the warehouse
    """,
    "category": 'Inventory',
    "depends": [
        'base',
        'product',
        'sale_stock'
    ],
    "data": [
        "security/stock_request_group.xml",
        "security/ir.model.access.xml",
        'views/stock_request_menu_view.xml',
        'views/stock_request_view.xml',
        "views/stock_request_line_view.xml",

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3'
}
