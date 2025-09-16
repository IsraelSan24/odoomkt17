{
    'name': 'ind_account',
    'summary': 'Modificaciones en account',
    'version': '17.0.1.0.1',
    'author': 'Juan Carlos León Huayta',
    'depends': [
        'account',
        'stock_account',
        'purchase_stock'
    ],
    'data': [
        'views/account_move.xml',  # Asegurar que el XML se cargue
        'views/account_move_line.xml',
        'views/account_payment.xml',
        'data/ir_sequence.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
