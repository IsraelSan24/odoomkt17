{
    'name': 'MKT Stock Picking - Guía de Remisión',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Customización para Guía de Remisión NUBEFACT',
    'description': 'Añade campos para generar Guía de Remisión según API NUBEFACT',
    'depends': ['stock', 'dv_l10n_pe_account_account', 'base'],
    'data': [
        'views/stock_picking_views.xml',
        'views/hr_employee_views.xml',

        'security/ir.model.access.csv',

        'data/pe.department.csv',
        'data/pe.province.csv',
        'data/pe.district.csv',
    ],
    'installable': True,
    'application': False,
}