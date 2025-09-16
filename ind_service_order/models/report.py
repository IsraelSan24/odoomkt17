from odoo import models, api


class ServiceOrderReport(models.AbstractModel):
    _name = 'report.service_order.print_service_order'
    _description = 'Reporte PDF Orden de Servicio'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['service.order'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'service.order',
            'docs': docs,
        }
