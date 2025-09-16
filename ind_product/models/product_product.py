from odoo import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.depends('default_code')
    def _compute_barcode(self):
        for record in self:
            record.barcode = record.default_code

    @api.onchange('default_code')
    def _onchange_default_code(self):
        if self.default_code:
            self.barcode = self.default_code
    
    @api.onchange('categ_id')
    def _onchange_classification_categ_id(self):
        print(self._origin.categ_id)
        all_category_id = 1  # Reemplaza con el ID real de la categoría 'All'
        if self._origin.categ_id and self._origin.categ_id.id != all_category_id:
            self.categ_id = self._origin.categ_id
