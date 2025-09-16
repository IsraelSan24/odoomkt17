{
    'name': 'Integración Nubefact',
    'version': '1.0',
    'summary': 'Integra Odoo con Nubefact para facturación electrónica',
    'description': 'Permite enviar facturas electrónicas a Nubefact desde Odoo.',
    'author': 'Israel Santana',
    'category': 'Accounting',
    'depends': ['account', 'ind_update_currency'], # Dependencia del módulo de contabilidad
    'data': [
        'views/account_move_views.xml',
        'views/nubefact_config_views.xml',
    ],
    'installable': True,
    'application': False,
}