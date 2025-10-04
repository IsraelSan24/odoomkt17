# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
###############################################################################

{
    "name": "Catalogos SUNAT",
    "version": "15.0.1",
    "author": "OPeru",
    "category": "Accounting & Finance",
    "summary": "Datos de Tablas para la factura electronica.",
    "license": "LGPL-3",
    "contributors": [
        'Soporte OPeru <soporte@operu.pe>',
    ],
    "description": """
Factura electronica - Datos Catalogos SUNAT.
====================================

Tablas:
--------------------------------------------
    * Tablas requeridas para los Documentos electronicos Peru

    """,
    "website": "http://www.operu.pe/contabilidad",
    "depends": [
        "base",
        "account",
        "l10n_pe",
    ],
    "data": [
        "data/document_type_data.xml",
        "data/identification_type_data.xml",
        "data/catalog_data.xml",
        "data/ple_table_data.xml",
        "views/catalog_views.xml",
        "views/table_views.xml",
        "security/ir.model.access.csv",   
    ],
    "images": [
        "static/description/banner.png",
    ],
    "installable": True,
    "auto_install": False,
    "sequence": 1,
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
}
