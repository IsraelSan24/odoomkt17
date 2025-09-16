from odoo import fields, models, api


class ParentProduct(models.Model):
    _name = 'producto.padre'
    _description = 'Parent Product'
    _rec_name = 'product_name'
    _sql_constraints = [('unique_original_product', 'UNIQUE(name)', 'El producto original ya existe.')]

    name = fields.Many2one(
        comodel_name='product.template',
        string='Producto Original',
        required=True,
        index=True,
    )
    calc_product = fields.Char( # TODO: DELETE IN V17
        string='Producto Original',
        compute='_compute_campo_calculado',
        store=True
    )
    product_alternativos = fields.Many2many(
        comodel_name='product.product',
        string='Productos alternativos',
        domain="[('id', '!=', name)]"
    )
    product_name = fields.Char(
        string='Nombre de producto',
        related='name.name'
    )
    product_reference = fields.Char(
        string='Referencia',
        related='name.default_code'
    )

    @api.depends('name') # TODO: DELETE IN V17
    def _compute_campo_calculado(self):
        for record in self:
            record.calc_product=record.name.name