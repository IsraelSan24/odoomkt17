from odoo import models, api, fields

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    service_conformity_id = fields.Many2many(
        'service.conformity',
        string='Conformidad de servicio',
        compute='_compute_service_conformity',
        copy=False,
        store=True
    )
    service_conformity_state = fields.Selection(
        string="Estado de conformidad",
        related="service_conformity_id.state",
        store=True,
        readonly=True
    )
   
    @api.depends(
      'order_line.purchase_request_lines.request_id.service_order_id.service_conformity_id',
      'service_conformity_id.state' 
    )
    def _compute_service_conformity(self):
       for record in self:
           service_conformities = record.order_line.purchase_request_lines.request_id.service_order_id.mapped(
               'service_conformity_id'
           )
           record.service_conformity_id = service_conformities[0] if service_conformities else False
    
    

    

    



