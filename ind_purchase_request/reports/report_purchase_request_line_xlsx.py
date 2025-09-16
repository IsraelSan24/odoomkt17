from odoo import models
from collections import defaultdict


class ReportPurchaseRequestLineXlsx(models.AbstractModel):
    _name = 'report.ind_purchase_request.report_rfq_line'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Report Purchase Request Line Xlsx'

    def _get_state_label(self, model, field, value):
        """Esta función se usa para obtener el label de los campos tipo selection"""
        model_obj = model._name
        
        field_obj = self.env[model_obj]._fields[field]
        selection_options = field_obj.selection
        
        if callable(selection_options):
            try:
                selection_options = selection_options(self.env[model_obj])
            except Exception as e:
                print(f"Error al obtener opciones de selección: {e}")
                field_info = field_obj.get_description(self.env)
                selection_options = field_info.get('selection', [])
        
        if selection_options and hasattr(selection_options, '__iter__'):
            state_dict = dict(selection_options)
            return state_dict.get(value)
        
        try:
            return field_obj.convert_to_export(value, self.env)
        except Exception:
            return value

    def _write_row(self, sheet, number_row, request_line, format):
        sheet.write(number_row, 0, number_row - 2)  # N°
        sheet.write(number_row, 1, request_line['id'])  # RFQ ID
        sheet.write(number_row, 2, request_line['rfq'])  # RFQ
        sheet.write(number_row, 3, request_line['rfq_state'])  # RFQ STATE
        sheet.write(number_row, 4, request_line['request_by'])  # REQUESTED BY
        sheet.write(number_row, 5, request_line['approved_by'])  # APPROVED BY
        sheet.write(number_row, 6, request_line['date_start'], format)  # DATE START
        sheet.write(number_row, 7, request_line['date_approved'], format)  # DATE APPROVED
        sheet.write(number_row, 8, request_line['request_type'])  # REQUEST TYPE
        sheet.write(number_row, 9, request_line['product_reference'])  # PRODUCT REFERENCE
        sheet.write(number_row, 10, request_line['product_name'])  # PRODUCT NAME
        sheet.write(number_row, 11, request_line['rfq_description'])  # RFQ LINE DESCRIPTION
        sheet.write(number_row, 12, request_line['analytic_code'])  # ANALYTIC CODE
        sheet.write(number_row, 13, request_line['analytic_name'])  # ANALYTIC NAME
        sheet.write(number_row, 14, request_line['product_qty'])  # PRODUCT QUANTITY
        sheet.write(number_row, 15, request_line['product_uom'])  # PRODUCT UOM NAME
        sheet.write(number_row, 16, request_line['estimated_cost'])  # ESTIMATED COST
        sheet.write(number_row, 17, request_line['order_status'])  # ORDER STATUS
        sheet.write(number_row, 18, request_line['order_line_id'])  # ORDER LINE ID
        sheet.write(number_row, 19, request_line['order_description'])  # ORDER DESCRIPTION
        sheet.write(number_row, 20, request_line['order_state'])  # ORDER STATE
        sheet.write(number_row, 21, request_line['order_product_qty'])  # ORDER PRODUCT QTY
        sheet.write(number_row, 22, request_line['order_user_requested'])  # ORDER USER REQUESTED
        sheet.write(number_row, 23, request_line['order_date_approved'], format)  # ORDER DATE APPROVED
        sheet.write(number_row, 24, request_line['picking_line_id'])  # PICKING LINE ID
        sheet.write(number_row, 25, request_line['picking_line_reference'])  # PICKING LINE REFERENCE
        sheet.write(number_row, 26, request_line['picking_state'])  # PICKING STATE
        sheet.write(number_row, 27, request_line['picking_date'], format)  # PICKING DATE
        sheet.write(number_row, 28, request_line['picking_qty'])  # PICKING QUANTITY
        sheet.write(number_row, 29, request_line['picking_type'])  # PICKING TYPE

    def generate_xlsx_report(self, workbook, data, rfq_lines):
        sheet = workbook.add_worksheet()

        title_format=workbook.add_format({
            'bold':True,
            'bg_color':'#edece7',
            'border':1,
            'align':'center',
            'valign':'vcenter',
            'font_size':14
            })
        header_format_rfq=workbook.add_format({
            'bold':True,
            'bg_color': '#154f99',
            'border':1,
            'font_size':12,
            'align':'center',
            'font_color':'white',
        })
        header_format_oc=workbook.add_format({
            'bold':True,
            'bg_color':'#154f99',
            'border':1,
            'font_size':12,
            'align':'center',
            'font_color':'white',
        })
        header_format_ing=workbook.add_format({
            'bold':True,
            'bg_color':'#154f99',
            'border':1,
            'font_size':12,
            'align':'center',
            'font_color':'white',
        })
        header_format = workbook.add_format({
            'bold': True,
            'bg_color':'#ef7c23',
            'border': 1,
            'font_size': 12,
            'align': 'center',
            'text_wrap': True,
        })
        date_format=workbook.add_format({'num_format':'dd/mm/yy'})

        sheet.set_row(3,30)
        sheet.set_column('C:C',15)
        sheet.set_column('D:D',15)
        sheet.set_column('E:E',35)
        sheet.set_column('F:F',35)
        sheet.set_column('G:G',15)
        sheet.set_column('H:H',20)
        sheet.set_column('I:I',20)
        sheet.set_column('J:J',15)
        sheet.set_column('K:K',50)
        sheet.set_column('L:L',65)
        sheet.set_column('M:M',15)
        sheet.set_column('N:N',60)
        sheet.set_column('O:O',11)
        sheet.set_column('P:P',15)
        sheet.set_column('Q:Q',11)
        sheet.set_column('R:R',15)
        sheet.set_column('S:S',10)
        sheet.set_column('T:T',15)
        sheet.set_column('U:U',13)
        sheet.set_column('V:V',13)
        sheet.set_column('W:W',35)
        sheet.set_column('X:X',13)
        sheet.set_column('Y:Y',10)
        sheet.set_column('Z:Z',20)
        sheet.set_column('AA:AA',12)
        sheet.set_column('AB:AB',13)
        sheet.set_column('AC:AC',13)
        sheet.set_column('AD:AD',13)
        
        sheet.merge_range('A1:AD1','REPORTE DE RFQ - ORDEN DE COMPRA - INGRESOS',title_format)
        sheet.merge_range('A2:R2','RFQ',header_format_rfq)
        sheet.merge_range('S2:X2','ORDEN DE COMPRA',header_format_oc)
        sheet.merge_range('Y2:AD2','INGRESOS',header_format_ing)

        ROW_HEADERS = 2
        PICKING_STATE = {
            'done': 'Realizado',
            'assigned': 'Listo',
            'confirmed': 'Esperando',
        }
        HEADERS = [
            'N°', 'LINEA DE RFQ', 'RFQ', 'ESTADO DE RFQ', 'SOLICITANTE', 'APROBADOR', 'FECHA DE CREACION RFQ', 'FECHA DE APROBACION', 'TIPO DE RFQ',
            'REFERENCIA INTERNA', 'PRODUCTO', 'DESCRIPCION', 'REFERENCIA C.C.', 'CENTRO DE COSTO', 'CANTIDAD', 'UNIDAD DE MEDIDA', 'COSTO ESTIMADO',
            'ESTADO DE PEDIDO', 'ID OC', 'REFERENCIA OC', 'ESTADO OC', 'CANTIDAD OC', 'RESPONSABLE', 'FECHA DE CREACION', 'ID INGRESO', 'REFERENCIA INGRESO',
            'ESTADO INGRESO', 'FECHA EFECTIVA', 'CANTIDAD HECHA', 'TIPO DE OPERACION'
        ]


        for row, header in enumerate(HEADERS, start=0):
            sheet.write(ROW_HEADERS, row, header, header_format)

        for row_line, request_line in enumerate(rfq_lines, 3):
            request_line_dict = defaultdict(str)

            ad_name, ad_code = [], []
            if request_line.analytic_distribution:
                for analytic_id, percentage in request_line.analytic_distribution.items():
                    analytic_account = self.env['account.analytic.account'].browse(int(analytic_id))
                    ad_name.append(analytic_account.name)
                    ad_code.append(analytic_account.code)   

            request_line_dict.update({
                'id': request_line.id,
                'rfq': request_line.request_id.name,
                'rfq_state': self._get_state_label(request_line, 'request_state', request_line.request_state),  # request_line.request_type
                'request_by': request_line.requested_by.name,
                'approved_by': request_line.approved_by.name,
                'date_start': request_line.date_start,
                'date_approved': request_line.date_approved,
                'request_type': self._get_state_label(request_line, 'request_type', request_line.request_type),  # request_line.request_type
                'product_reference': request_line.product_id.default_code,
                'product_name': request_line.product_id.name,
                'rfq_description': request_line.name,
                'analytic_code': str(ad_code),
                'analytic_name': str(ad_name),
                'product_qty': request_line.product_qty,
                'product_uom': request_line.product_uom_id.name,
                'estimated_cost': request_line.estimated_cost,
                'order_status': self._get_state_label(request_line, 'order_status', request_line.order_status)  # request_line.order_status
            })

            if not request_line.purchase_lines:
                self._write_row(sheet, row_line, request_line_dict, date_format)
                continue

            for order_line in request_line.purchase_lines:
                request_line_dict.update({
                    'order_line_id': order_line.id,
                    'order_description': order_line.order_id.name,
                    'order_state': order_line.order_id.state,
                    'order_product_qty': order_line.product_qty,
                    'order_user_requested': order_line.order_id.user_id.name,
                    'order_date_approved': order_line.order_id.date_approve,
                })
                if not order_line.move_ids:
                    self._write_row(sheet, row_line, request_line_dict, date_format)
                    continue

                filtered_moves = order_line.move_ids.filtered(lambda sm: sm.state in ('assigned', 'done', 'confirmed'))

                for picking_line in filtered_moves:
                    if picking_line.state in ('assigned', 'done', 'confirmed') and picking_line.location_dest_id.usage == 'internal':
                        request_line_dict.update({
                            'picking_line_id': picking_line.id,
                            'picking_line_reference': picking_line.reference,
                            'picking_state': PICKING_STATE[picking_line.state],
                            'picking_date': picking_line.picking_id.date_done if picking_line.state == 'done' else '',
                            'picking_qty': picking_line.product_uom_qty if picking_line.state == 'done' else '',
                            'picking_type': 'Ingreso' if picking_line.state == 'done' else '',
                        })
                        self._write_row(sheet, row_line, request_line_dict, date_format)
