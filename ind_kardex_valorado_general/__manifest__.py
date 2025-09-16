{
    'name': 'Indomin - Kardex Valorado General',
    'description':'Reporte de Kardex Valorado a nivel del almacen',
    'author': 'Juan Carlos León Huayta',
    'version': '17.0.0.1.0',
    'depends':[
        "base",
        "stock",
        "purchase_request",
        "account",
        "product",
        "stock_move_invoice"
    ],
    'data':[
        "security/res_group.xml",
        "models/kardexval_general.xml",
        "security/ir_model_access.xml",
        "views/stock_move.xml",
        "views/account_account.xml"
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
