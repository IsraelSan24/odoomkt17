from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    pickup_request_ids = fields.One2many(
        comodel_name='pickup.request', 
        inverse_name='purchase_order_id', 
        string="Solicitudes de Recojo"
    )
    
    def action_create_pickup_request(self):
        self.ensure_one()

        if self.pickup_request_ids:
            title = '⚠ Advertencia'
            type = 'warning'
            messaje = 'Esta orden de compra ya tiene una o más solicitudes de recojo.'
      
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': title,
                    'type': type,
                    'message': messaje,
                    'sticky': False,
                    'next': {
                        'type': 'ir.actions.act_window',
                        'res_model': 'pickup.request',
                        'view_mode': 'form',
                        'views': [(False, 'form')],  # <- ESTA LÍNEA ES CLAVE
                        'target': 'new',
                        'context': {
                            'default_purchase_order_id': self.id,
                        },
                    },
                }
            }
        else:
            return {
                'name': 'Crear Solicitud de Recojo',
                'type': 'ir.actions.act_window',
                'res_model': 'pickup.request',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_purchase_order_id': self.id,  # Cargar automáticamente la OC actual
                }
            }
