from odoo import fields,models


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    num_transferencia = fields.Char(string='N° Op. Bancaria')
    factura_pagar = fields.Char(string='N° Documento')
    fecha_documento = fields.Date(string='Fecha de documento')
    fecha_vencimiento = fields.Date(string='Fecha de vencimiento')
    tipo_documento = fields.Char(string='Tipo de documento')
