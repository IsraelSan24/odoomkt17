# -*- coding: utf-8 -*-
###############################################################################
#    Hooks compatibles Odoo 15/16 y 17/18
###############################################################################
import logging
from os.path import join, dirname, realpath

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


# --- Helpers -----------------------------------------------------------------
def _load_catalog_03_data(cr):
    csv_path = join(dirname(realpath(__file__)), "data", "l10n_pe_edi.catalog.03.csv")
    with open(csv_path, "rb") as csv_file:
        # saltar cabecera
        csv_file.readline()
        cr.copy_expert(
            """COPY l10n_pe_edi_catalog_03 (code, name, active)
               FROM STDIN WITH DELIMITER '|'""",
            csv_file,
        )
    # xml_ids
    cr.execute(
        """
        INSERT INTO ir_model_data (name, res_id, module, model, noupdate)
        SELECT concat('l10n_pe_edi_cat03_', code), id, 'l10n_pe_edi_catalog',
               'l10n_pe_edi.catalog.03', 't'
        FROM l10n_pe_edi_catalog_03
        """
    )


def _load_catalog_25_data(cr):
    csv_path = join(dirname(realpath(__file__)), "data", "l10n_pe_edi.catalog.25.csv")
    with open(csv_path, "rb") as csv_file:
        # saltar cabecera
        csv_file.readline()
        cr.copy_expert(
            """COPY l10n_pe_edi_catalog_25 (code, name, active)
               FROM STDIN WITH DELIMITER '|'""",
            csv_file,
        )
    # xml_ids
    cr.execute(
        """
        INSERT INTO ir_model_data (name, res_id, module, model, noupdate)
        SELECT concat('l10n_pe_edi_cat25_', code), id, 'l10n_pe_edi_catalog',
               'l10n_pe_edi.catalog.25', 't'
        FROM l10n_pe_edi_catalog_25
        """
    )


# --- Hooks (compatibles) -----------------------------------------------------
def post_init_hook(cr_or_env, registry=None):
    """
    Odoo 15/16: firma (cr, registry)
    Odoo 17/18: firma (env)
    """
    if hasattr(cr_or_env, "cr"):           # 17/18
        env = cr_or_env
    else:                                   # 15/16
        cr = cr_or_env
        env = api.Environment(cr, SUPERUSER_ID, {})

    cr = env.cr
    _logger.info("l10n_pe_edi_catalog: cargando catálogos 03 y 25 (post_init_hook)")
    _load_catalog_03_data(cr)
    _load_catalog_25_data(cr)
    _logger.info("l10n_pe_edi_catalog: catálogos cargados correctamente.")


def uninstall_hook(cr_or_env, registry=None):
    """
    Odoo 15/16: firma (cr, registry)
    Odoo 17/18: firma (env)
    """
    if hasattr(cr_or_env, "cr"):           # 17/18
        env = cr_or_env
    else:                                   # 15/16
        cr = cr_or_env
        env = api.Environment(cr, SUPERUSER_ID, {})

    cr = env.cr
    _logger.warning("l10n_pe_edi_catalog: limpiando catálogos (uninstall_hook)")
    cr.execute("DELETE FROM l10n_pe_edi_catalog_03;")
    cr.execute("DELETE FROM ir_model_data WHERE model = 'l10n_pe_edi.catalog.03';")
    cr.execute("DELETE FROM l10n_pe_edi_catalog_25;")
    cr.execute("DELETE FROM ir_model_data WHERE model = 'l10n_pe_edi.catalog.25';")
