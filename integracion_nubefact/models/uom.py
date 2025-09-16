from odoo import models, fields

class UomUom(models.Model):
    _inherit = 'uom.uom'

    sunat_code = fields.Char(string="Código SUNAT")