from odoo import api, fields, models, Command


class ProductProduct(models.Model):
    _inherit = 'product.product'

    productos_padre = fields.Many2many(
        comodel_name='producto.padre',
        relation = "ind_pro_padre_pro_pro_prd_pad_rel",
        column1 = "product_id",
        column2 = "product_padre_id",
        string='Productos Originales',
        store=True,
        compute='_compute_parent_products_ids'
    )

    @api.depends('productos_padre')
    def _compute_parent_products_ids(self):
        for record in self:
            parent_products = self.env['producto.padre'].search([
                ('product_alternativos', 'in', record.id)
            ])
            record.productos_padre = [Command.set(parent_products)]
