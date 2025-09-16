from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    fecha_doc = fields.Date(string='Fecha de documento')
    fecha_vence = fields.Date(string='Fecha de vencimiento')
    tipo_documento = fields.Char(string='Documento')
