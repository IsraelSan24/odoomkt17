from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    date = fields.Datetime(string="Date", default=fields.Datetime.now, required=True)