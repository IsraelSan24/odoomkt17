from odoo import fields, models

class AccountJournal(models.Model):
    _inherit = 'account.journal'
    
    default_compra=fields.Boolean(string="Compra",default=False)
    default_venta=fields.Boolean(string="Venta",default=False)