from odoo import fields, models

# TODO: DELETE IN V17
class Users(models.Model):
    _inherit = 'res.users'
    
    planning = fields.Boolean(string="Área de Planeamiento", default=False)
