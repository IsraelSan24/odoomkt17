from odoo import models
from odoo.tools import html2plaintext


class PickupRequestXlsx(models.AbstractModel):
    _name = 'report.ind_purchase_pickup_request.pickup_report'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Reporte Recojos'

    def generate_xlsx_report(self, workbook, data, requests):
        sheet = workbook.add_worksheet('Solicitudes de Recojo')
        title_format = workbook.add_format({
            'bold': True, 'bg_color': '#edece7', 'border': 1, 'align': 'center',
            'valign': 'vcenter', 'font_size': 14
        })
        header_format = workbook.add_format({
            'bold': True, 'bg_color': '#154f99', 'border': 1, 'font_size': 12,
            'align': 'center', 'font_color': 'white'
        })
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        text_wrap_format = workbook.add_format({'text_wrap': True})

        # Títulos
        sheet.merge_range('A1:S1', 'Reporte de Solicitudes de Recojo', title_format)

        headers = [
            "Fecha y Hora Solicitud", "Solicitado Por", "RFQ Origen", "Proveedor", "RUC",
            "Orden de Compra", "Observaciones", "Horario Laboral", "Dirección del Proveedor",
            "Dirección de Entrega", "Tipo de Solicitud", "Modalidad", "Urgencia",
            "Conductor", "Observaciones de Almacén", "Estado", "Ingresos", "Guía",
            "Fecha de Ingreso", "Diferencia en Días", "Estado de Liquidación", "Número de Factura"
        ]
        for col, header in enumerate(headers):
            sheet.write(1, col, header, header_format)

        # Ajustar tamaños de columna
        column_widths = [23, 15, 20, 20, 12, 20, 30, 18, 25, 25, 15, 12, 12, 15, 30, 15, 20, 15, 18, 18, 23, 18]
        for col, width in enumerate(column_widths):
            sheet.set_column(col, col, width)

        # Datos
        row = 2
        for request in requests.sudo():
            sheet.write(row, 0, request.pickup_datetime or '', date_format)
            sheet.write(row, 1, ', '.join(request.requested_by.sudo().mapped('name')))
            sheet.write(row, 2, ', '.join(request.purchase_request_ids.sudo().mapped('name')))
            sheet.write(row, 3, request.partner_id.sudo().name or '')
            sheet.write(row, 4, request.partner_vat or '')
            sheet.write(row, 5, request.purchase_order_id.sudo().name or '')
            sheet.write(row, 6, html2plaintext(request.observations or ''), text_wrap_format)
            sheet.write(row, 7, request.work_time or '')
            sheet.write(row, 8, request.partner_street or '')
            sheet.write(row, 9, request.delivery_address_id.sudo().name or '')
            sheet.write(row, 10, dict(request._fields['request_type'].selection).get(request.request_type, ''))
            sheet.write(row, 11, dict(request._fields['modality'].selection).get(request.modality, ''))
            sheet.write(row, 12, dict(request._fields['urgency'].selection).get(request.urgency, ''))
            sheet.write(row, 13, request.driver_id.sudo().name or '')
            sheet.write(row, 14, html2plaintext(request.warehouse_observations or ''), text_wrap_format)
            sheet.write(row, 15, dict(request._fields['status'].selection).get(request.status, ''))
            sheet.write(row, 16, ', '.join(request.picking_ids.sudo().mapped('name')))
            sheet.write(row, 17, request.guia or '')
            sheet.write(row, 18, request.date_done or '', date_format)
            sheet.write(row, 19, request.days_difference or 0)
            sheet.write(row, 20, dict(request._fields['liquidation_status'].selection).get(request.liquidation_status, ''))
            sheet.write(row, 21, request.invoice_number or '')
            row += 1
