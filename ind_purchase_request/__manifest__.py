{
    'name': 'Indomin - Solicitud de Compra',
    'author': 'Dany Chavez',
    'version': '17.0.1.0.0', # 15.0.1.1.0
    'summary': 'Cambios aplicados para el módulo Purchase Request',
    'category': 'Purchase Management',
    'depends': [
        'analytic_partner_history',
        'purchase_request',
        'report_xlsx',
        'hr',
        'purchase_stock',
        'account',
        'analytic'
    ],
    'data': [
        'security/purchase_request_security.xml',
        'security/purchase_order_security.xml',
        'security/ir.model.access.csv',
        'reports/ir_actions_report_templates.xml',
        'reports/ir_actions_report.xml',
        'wizards/purchase_request_line_make_purchase_order.xml',
        'views/purchase_order_line_views.xml',
        'views/purchase_order_views.xml',
        'views/purchase_request_line_views.xml',
        'views/purchase_request_views.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'ind_purchase_request/static/src/overrides/**/*',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
