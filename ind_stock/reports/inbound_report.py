from odoo import models


class PartnerXlsx(models.AbstractModel):
    _name = 'report.ind_stock.reporte_ingresos'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Reporte Ingresos'

    def generate_xlsx_report(self, workbook, data, picking):
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
            'bg_color':'yellow',
            'border': 1,
            'font_size': 10,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
        })
        date_format=workbook.add_format({'num_format':'dd/mm/yy'})
        saltolinea_format = workbook.add_format({'text_wrap':True})
        
        sheet.set_row(3,30)
        sheet.set_column('A:A',5)
        sheet.set_column('B:B',12)
        sheet.set_column('C:C',18)
        sheet.set_column('D:D',9)
        sheet.set_column('E:E',10)
        sheet.set_column('F:F',10)
        sheet.set_column('G:G',12)
        sheet.set_column('H:H',13)
        sheet.set_column('I:I',10)
        sheet.set_column('J:J',18)
        sheet.set_column('K:K',8)
        sheet.set_column('L:L',8)
        sheet.set_column('M:M',10)
        sheet.set_column('N:N',10)
        sheet.set_column('O:O',10)
        sheet.set_column('P:P',12)
        sheet.set_column('Q:Q',12)

        """ SALIDAS - 1
        ID - 2
        GUÍA O FACTURA - 3
        CÓDIGO PRODUCTO - 4
        CENTRO DE COSTO - 5
        PRECIO - 6 """
        
        sheet.merge_range('A1:L1','REPORTE DE INGRESOS',title_format)
        sheet.write(1,0,"N°",header_format)
        sheet.write(1,1,"REFERENCIA",header_format)
        sheet.write(1,2,"PRODUCTO",header_format)
        sheet.write(1,3,"CANTIDAD",header_format)
        sheet.write(1,4,"FECHA DE CREACION",header_format)
        sheet.write(1,5,"FECHA EFECTIVA",header_format)
        sheet.write(1,6,"DOCUMENTO DE REFERENCIA",header_format)
        sheet.write(1,7,"REQUERIMIENTO",header_format)
        sheet.write(1,8,"FECHA DE CREACIÓN DE RFQ",header_format)
        sheet.write(1,9,"PROVEEDOR",header_format)
        sheet.write(1,10,"COSTO TOTAL",header_format)
        sheet.write(1,11,"COSTO UNITARIO",header_format)
        sheet.write(1,12,"ORDEN DE COMPRA",header_format)
        sheet.write(1,13,"GUIA",header_format)
        sheet.write(1,14,"FACTURA",header_format)
        sheet.write(1,15,"ORIGEN",header_format)
        sheet.write(1,16,"DESTINO",header_format)
        sheet.write(1,17,"CENTRO DE COSTO",header_format)
        
        row=2
        for data in picking:
            if data.state == 'done':
                for line in data.move_ids_without_package:
                    product_code = line.product_id.code
                    product_name = line.product_id.name
                    pra_records = self.env['purchase.request.allocation'].search([('stock_move_id','=',line.id)])
                    if line.state == 'cancel':
                        continue
                    
                    if pra_records:
                        pra=pra_records[0]
                        if data.location_id.usage == 'supplier' and data.location_dest_id.usage == 'internal':
                            sheet.write(row, 0, int(row - 1))
                            sheet.write(row, 1, data.name)
                            sheet.write(row, 2, f"[{product_code}]{product_name}")
                            sheet.write(row, 3, line.quantity_done)
                            sheet.write(row, 4, line.picking_id.create_date or "",date_format)
                            sheet.write(row, 5, line.date or "",date_format)
                            sheet.write(row, 6, line.picking_id.origin)
                            sheet.write(row, 7, pra.purchase_request_line_id.request_id.name)
                            sheet.write(row, 8, pra.purchase_request_line_id.request_id.create_date or "",date_format)
                            sheet.write(row, 9, line.purchase_line_id.order_id.partner_id.name)
                            sheet.write(row, 10, line.monto_asiento)
                            sheet.write(row, 11, line.precio_unit_asiento)
                            sheet.write(row, 12, line.purchase_line_id.order_id.name)
                            sheet.write(row, 13, line.picking_id.guia or "")
                            sheet.write(row, 14, line.picking_id.factura or "")
                            sheet.write(row, 15, line.location_id.name)
                            sheet.write(row, 16, line.location_dest_id.name)
                            sheet.write(row, 17, "N/A")  #TODO: CENTER COST
                            row += 1
                            
                        else:
                            if data.location_id.usage == 'internal' and data.location_dest_id.usage == 'supplier':
                                sheet.write(row, 0, int(row - 1))
                                sheet.write(row, 1, data.name)
                                sheet.write(row, 2, f"[{product_code}]{product_name}")
                                sheet.write(row, 3, line.quantity_done*(-1))
                                sheet.write(row, 4, line.picking_id.create_date or "",date_format)
                                sheet.write(row, 5, line.date or "",date_format)
                                sheet.write(row, 6, line.picking_id.origin)
                                sheet.write(row, 7, pra.purchase_request_line_id.request_id.name)
                                sheet.write(row, 8, pra.purchase_request_line_id.request_id.create_date or "",date_format)
                                sheet.write(row, 9, line.purchase_line_id.order_id.partner_id.name)
                                sheet.write(row, 10, line.monto_asiento*(-1))
                                sheet.write(row, 11, line.precio_unit_asiento)
                                sheet.write(row, 12, line.purchase_line_id.order_id.name)
                                sheet.write(row, 13, line.picking_id.guia or "")
                                sheet.write(row, 14, line.picking_id.factura or "")
                                sheet.write(row, 15, line.location_id.name)
                                sheet.write(row, 16, line.location_dest_id.name)
                                sheet.write(row, 17, "N/A")  #TODO: CENTER COST
                                row += 1

                    else:
                        if data.location_id.usage == 'supplier' and data.location_dest_id.usage == 'internal':
                            sheet.write(row, 0, int(row - 1))
                            sheet.write(row, 1, data.name)
                            sheet.write(row, 2, f"[{product_code}]{product_name}")
                            sheet.write(row, 3, line.quantity_done)
                            sheet.write(row, 4, line.picking_id.create_date or "",date_format)
                            sheet.write(row, 5, line.date or "",date_format)
                            sheet.write(row, 6, line.picking_id.origin)
                            sheet.write(row, 7, "")
                            sheet.write(row, 8, "")
                            sheet.write(row, 9, line.purchase_line_id.order_id.partner_id.name)
                            sheet.write(row, 10, line.monto_asiento)
                            sheet.write(row, 11, line.precio_unit_asiento)
                            sheet.write(row, 12, line.purchase_line_id.order_id.name)
                            sheet.write(row, 13, line.picking_id.guia or "")
                            sheet.write(row, 14, line.picking_id.factura or "")
                            sheet.write(row, 15, line.location_id.name)
                            sheet.write(row, 16, line.location_dest_id.name)
                            sheet.write(row, 17, "N/A")  #TODO: CENTER COST
                            row += 1
                            
                        else:
                            if data.location_id.usage == 'internal' and data.location_dest_id.usage == 'supplier':
                                sheet.write(row, 0, int(row - 1))
                                sheet.write(row, 1, data.name)
                                sheet.write(row, 2, f"[{product_code}]{product_name}")
                                sheet.write(row, 3, line.quantity_done*(-1))
                                sheet.write(row, 4, line.picking_id.create_date or "",date_format)
                                sheet.write(row, 5, line.date or "",date_format)
                                sheet.write(row, 6, line.picking_id.origin)
                                sheet.write(row, 7, "")
                                sheet.write(row, 8, "")
                                sheet.write(row, 9, line.purchase_line_id.order_id.partner_id.name)
                                sheet.write(row, 10, line.monto_asiento*(-1))
                                sheet.write(row, 11, line.precio_unit_asiento)
                                sheet.write(row, 12, line.purchase_line_id.order_id.name)
                                sheet.write(row, 13, line.picking_id.guia or "")
                                sheet.write(row, 14, line.picking_id.factura or "")
                                sheet.write(row, 15, line.location_id.name)
                                sheet.write(row, 16, line.location_dest_id.name)
                                sheet.write(row, 17, "N/A")  #TODO: CENTER COST
                                row += 1