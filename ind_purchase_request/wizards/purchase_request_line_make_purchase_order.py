from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order"

    keep_description_order = fields.Boolean(string="Mantener descripcion en todos los items")

    @api.onchange('keep_description_order')
    def _onchange_keep_description_order(self):
        if self.keep_description_order:
            for line in self.item_ids:
                line.keep_description = True
        else:
            for line in self.item_ids:
                line.keep_description = False

    # OVERRIDE
    @api.model_create_multi
    def _check_valid_request_line(self, request_line_ids):
        picking_type = False
        company_id = False
        for line in self.env["purchase.request.line"].browse(request_line_ids):
            if line.request_state == "done":
                raise UserError(_("The purchase has already been completed."))
            if line.request_state != "approved":
                # START OVERRIDE
                raise UserError(
                    _("Purchase Requeste {} with item {} is not approved").format(line.request_id.name, line.name)
                )
                # END OVERRIDE

            if line.purchase_state == "done":
                raise UserError(_("The purchase has already been completed."))

            line_company_id = line.company_id and line.company_id.id or False
            if company_id is not False and line_company_id != company_id:
                raise UserError(_("You have to select lines from the same company."))
            else:
                company_id = line_company_id

            line_picking_type = line.request_id.picking_type_id or False
            if not line_picking_type:
                raise UserError(_("You have to enter a Picking Type."))
            if picking_type is not False and line_picking_type != picking_type:
                raise UserError(
                    _("You have to select lines from the same Picking Type.")
                )
            else:
                picking_type = line_picking_type

    def _check_same_location(self):
        """Valida que todas las líneas pertenezcan a solicitudes con la misma ubicación."""
        request_ids = self.item_ids.mapped('line_id.request_id')
        location_values = request_ids.mapped('location_id')  # Esto es una lista de valores (no recordsets)
        
        unique_location_values = set(location_values)  # No necesitas .ids
        if len(unique_location_values) > 1:
            raise UserError("Las solicitudes de compra deben tener la misma ubicación.")
        
        classification_values = request_ids.mapped('classification_rfq')  # También devuelve una lista de strings
        unique_classification_values = set(classification_values)
        if len(unique_classification_values) > 1:
            raise UserError("Las solicitudes de compra deben tener la misma clasificación.")

    def make_purchase_order(self):
        for item in self.item_ids:
            if item.product_qty + item.count_order > item.count_rfq:
                raise UserError(
                    f"La cantidad solicitada para el producto '{item.product_id.display_name}' "
                    f"excede la requerida.\n\n"
                    f"Requerido: {item.count_rfq}, "
                    f"Ya ordenado: {item.count_order}, "
                    f"A solicitar: {item.product_qty}"
                )
                
        self._check_same_location()
        
        if self.purchase_order_id:
            request_ids = self.item_ids.mapped('line_id.request_id')
            po_location = self.purchase_order_id.location_id
            request_locations = request_ids.mapped('location_id')

            po_clasificacion = self.purchase_order_id.classification_rfq

            request_classificacion = request_ids.mapped('classification_rfq')

            unique_request_locations = set(request_locations)
            unique_request_clasificacion = set(request_classificacion)

            if po_location:
                if len(unique_request_locations) > 1 or po_location not in unique_request_locations:
                    raise UserError(_("La ubicación del pedido de compra no coincide con la de las solicitudes."))
            
            if po_clasificacion:
                if len(unique_request_clasificacion) > 1 or po_clasificacion not in unique_request_clasificacion:
                    raise UserError(_("La clasificacion del pedido de compra no coincide con la de las solicitudes."))

        res = super().make_purchase_order()

        return res
