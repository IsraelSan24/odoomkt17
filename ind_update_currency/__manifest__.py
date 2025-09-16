# -*- coding: utf-8 -*-
{
    'name': 'Indomin - Actualización de Tipo de Cambio',
    'version': '17.0.1.0.0',
    'author': 'Dany Chavez',
    'category': 'Extra Tools',
    'sequence': 10,
    'summary': """
    Este módulo actualiza el tipo de cambio de manera diaria y masiva, ya sea a través de una acción programada o mediante un botón, según se requiera
    """,
    'description': '',
    'depends': [
        'ind_api_token',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'wizards/res_currency_day_update_views.xml',
        'views/res_currency_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
