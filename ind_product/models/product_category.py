from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    classification_rfq = fields.Selection(
        selection=[
            ('service', 'Servicio'),
            ('products', 'Productos'),
            ('fixed_assets', 'Activo fijo'),
            ('rental_service', 'Servicio de alquiler')
        ],
        string='Clase de RFQ',
        index=True
    )

    @api.onchange('classification_rfq')
    def _onchange_classification_rfq(self):
        if self._origin.classification_rfq:
            self.classification_rfq = self._origin.classification_rfq

    #solo se puede eliminar la categoria si no tiene ningun rfq asociado
    def unlink(self):
        # Buscar líneas de solicitud de compra vinculadas a esta categoría
        PurchaseRequestLine = self.env['purchase.request.line']
        linked_lines = PurchaseRequestLine.search([('product_id.categ_id.name', '=', self.name)])

        if linked_lines:
            raise UserError('Debes eliminar todas las líneas de solicitud de compra vinculadas a esta categoría antes de eliminarla.')
        
        # Si no hay líneas vinculadas, proceder con la eliminación
        return super(ProductCategory, self).unlink()
