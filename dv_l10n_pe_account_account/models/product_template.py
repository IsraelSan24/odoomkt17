from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # TODO REFACTOR
    can_be_expensed = fields.Boolean(string="Es un gasto", compute='_compute_can_be_expensed',
        store=True, readonly=False, help="Artículo que es un gasto.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # When creating an expense product on the fly, you don't expect to
            # have taxes on it
            if vals.get('can_be_expensed', False):
                vals.update({'supplier_taxes_id': False})
        return super(ProductTemplate, self).create(vals_list)

    @api.depends('type')
    def _compute_can_be_expensed(self):
        self.filtered(lambda p: p.type not in ['consu', 'service']).update({'can_be_expensed': False})