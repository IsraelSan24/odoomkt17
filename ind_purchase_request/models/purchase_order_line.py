from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        """Este método se tuvo que modificar para poder agregar la distribución analitica de cada purchase.line """
        res = super(PurchaseOrderLine, self)._prepare_stock_move_vals(picking, price_unit, product_uom_qty, product_uom)
        res['analytic_distribution'] = self.analytic_distribution
        return res

    @api.constrains('product_qty')
    def _check_requested_qty_limit(self):
        for line in self:
            if not line.purchase_request_lines:
                continue

            # Sumar la cantidad total solicitada para este producto
            total_requested = sum(
                req_line.product_qty
                for req_line in line.purchase_request_lines
                if req_line.product_id == line.product_id
            )

            # Sumar la cantidad total comprada en otras líneas de OC que compartan las mismas solicitudes
            existing_po_lines = self.env['purchase.order.line'].search([
                ('id', '!=', line.id),
                ('product_id', '=', line.product_id.id),
                ('purchase_request_lines', 'in', line.purchase_request_lines.ids),
                ('state', '!=', 'cancel')
            ])

            total_ordered = sum(existing_line.product_qty for existing_line in existing_po_lines)

            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

            if float_compare(total_ordered + line.product_qty, total_requested, precision_digits=precision) > 0:
                raise ValidationError(
                    f'La cantidad total del producto "{line.product_id.display_name}" '
                    f'supera lo solicitado ({total_requested}). Ya se han ordenado {total_ordered}.'
                )