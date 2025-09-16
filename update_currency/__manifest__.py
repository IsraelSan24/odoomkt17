# -*- coding: utf-8 -*-

{
    'name': 'Currency Update',
    'version': '17.0.1.0.0',
    'author': 'Israel Santana',
    'category': 'Extra Tools',
    'sequence': 10,
    'summary': 'Actualiza el tipo de cambio mediante una acción programada',
    'description': "",
    'depends': [
        'base_setup', 'mkt_documental_managment'
    ],
    'data': [
        'data/ir_cron.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
