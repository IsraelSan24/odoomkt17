{
    'name': 'Analytic Partner History',
    'version': '17.0.1.0.0',
    'summary': 'Historial de clientes asignados a centros de costo',
    'author': 'Israel Santana',
    'maintainer': 'Dany Chavez',
    'category': 'Accounting',
    'depends': [
        'account_accountant'
    ],
    'data': [
        'security/analytic_partner_history_security.xml',
        'security/ir.model.access.csv',
        'views/account_analytic_account_partner_history_views.xml',
        'views/account_analytic_account_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
