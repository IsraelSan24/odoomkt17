from odoo.exceptions import ValidationError, UserError
from odoo import models, fields


class Picking(models.Model):
    _inherit = 'stock.picking'
    
    guia = fields.Char(string='Guia')
    factura = fields.Char(string='Factura')

    def button_validate(self):
        for record in self:
            # Verificar si picking_type_id es 32, si es así, validar automáticamente
            if record.location_id.usage == 'internal':
                return super(Picking, self).button_validate()

            if record.group_id and record.purchase_id:
                if not record.guia and not record.factura:
                    raise ValidationError('Debes Ingresar una guia o factura.')

                # Inicializar las cantidades pendientes de cada línea de la orden de compra

                pending_quantities = {
                    line.id: round(line.product_qty - line.qty_received,3)
                    for line in record.purchase_id.order_line
                }

                # Diccionario para acumular las cantidades hechas por producto
                done_quantities = {}

                # Iterar sobre las líneas del picking y validar las cantidades
                for move_line in record.move_line_ids:
                    product_id = move_line.product_id.id
                    qty_done = move_line.qty_done

                    # Actualizar las cantidades hechas por producto
                    if product_id not in done_quantities:
                        done_quantities[product_id] = qty_done
                    else:
                        done_quantities[product_id] += qty_done

                    # Buscar líneas de orden de compra para el producto actual
                    matching_lines = [
                        line_id for line_id, qty in pending_quantities.items()
                        if record.purchase_id.order_line.browse(line_id).product_id.id == product_id and qty > 0
                    ]

                    if not matching_lines:
                        product_name = move_line.product_id.display_name
                        raise ValidationError(
                            f'No hay suficientes cantidades disponibles en la orden de compra para el producto {product_name}.'
                        )

                    # Validar y restar las cantidades de las líneas coincidentes
                    for line_id in matching_lines:

                        if qty_done <= pending_quantities[line_id]:
                            pending_quantities[line_id] -= qty_done
                            qty_done = 0
                            break
                        else:
                            qty_done -= pending_quantities[line_id]
                            pending_quantities[line_id] = 0

                    if qty_done > 0:
                        product_name = move_line.product_id.display_name
                        raise ValidationError(
                            f'La cantidad hecha para el producto {product_name} excede la cantidad en la orden de compra.'
                        )

                # Verificar que las cantidades hechas no excedan las cantidades en la orden de compra
                for product_id, done_qty in done_quantities.items():
                    total_order_qty = sum(
                        line.product_qty for line in record.purchase_id.order_line
                        if line.product_id.id == product_id
                    )
                    if done_qty > total_order_qty:
                        product_name = self.env['product.product'].browse(product_id).display_name
                        raise ValidationError(
                            f'La cantidad total hecha para el producto {product_name} excede la cantidad en la orden de compra.'
                        )

        return super(Picking, self).button_validate()


    def unlink(self):
        for picking in self:
            if picking.state in ('done', 'assigned', 'waiting', 'confirmed', 'cancel'):
                raise UserError('No se puede eliminar un albarán que no este en estado Borrador')
        return super(Picking,self).unlink()
        