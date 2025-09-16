{
    'name': 'Solicitudes de trabajo',
    'version': '17.0.1.0.0', # 15.0.0.0.13
    'author': 'Dany Chavez',
    'category': 'Purchase',
    'depends': [
        'base',
        'purchase',
        'purchase_request',
        'ind_purchase_request',
        'ind_purchase_pickup_request',
        'account_budget'
    ],
    'data': [
        'security/service_order_security.xml',
        'security/ir.model.access.csv',
        'security/service_order.xml',
        'data/ir_sequence_data.xml',
        'reports/service_order_templates.xml',
        'reports/service_conformity_templates.xml',
        'reports/ir_actions_report.xml',
        'views/purchase_request_views.xml',
        'views/account_analytic_account_views.xml',
        'views/service_order_views.xml',
        'views/service_conformity_views.xml',
        'views/service_order_menus.xml',
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
