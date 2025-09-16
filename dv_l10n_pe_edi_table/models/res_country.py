from odoo import models, fields


class ResCountry(models.Model):
    _inherit = 'res.country'

    l10n_pe_edi_table_35_id = fields.Many2one('l10n_pe_edi.table.35', string="Codigo País", help="Tabla 35")