# -*- coding: utf-8 -*-

{
    'name': 'Indomin - API Token',
    'version': '17.0.1.0.0',
    'author': 'Dany Chavez',
    'category': 'Extra Tools',
    'sequence': 10,
    'summary': 'Módulo que agrega la funcionalidad de integrar odoo con API.net para consultas de RUC, DNI y Tipo de cambio',
    'description': "",
    'depends': [
        'base_setup'
    ],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
