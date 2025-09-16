from odoo import models, api, fields
#import logging

#_logger = logging.getLogger(__name__)  # Definir el logger


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'
    
    service_order_id = fields.One2many(
        comodel_name='service.order',
        inverse_name='purchase_request_id',
        string='Orden de Trabajo',

    )
    service_order_state = fields.Selection(
        string='Service Order State',
        related='service_order_id.state',
        store=True
    )

    def action_view_service_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'OT',
            'view_mode': 'form',
            'res_model': 'service.order',
            'res_id': self.service_order_id.id,
            'target': 'current'
        }
