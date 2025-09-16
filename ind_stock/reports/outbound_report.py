from odoo import models
from odoo.tools import html2plaintext


class PartnerXlsx(models.AbstractModel):
    _name = 'report.ind_stock.reporte_salidas'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Reporte salidas'

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
            'bg_color':'#ef7c23',
            'border': 1,
            'font_size': 12,
            'align': 'center',
            'text_wrap': True,
        })
        date_format=workbook.add_format({'num_format':'dd/mm/yy'})
        saltolinea_format = workbook.add_format({'text_wrap':True})
        
        sheet.set_row(3,30)
        sheet.set_column('A:A',8)
        sheet.set_column('B:B',18)
        sheet.set_column('C:C',13)
        sheet.set_column('D:D',13)
        sheet.set_column('E:E',14)
        sheet.set_column('F:F',18)
        sheet.set_column('G:G',10)
        sheet.set_column('H:H',15)
        sheet.set_column('I:I',8)
        sheet.set_column('J:J',8)
        sheet.set_column('K:K',8)
        sheet.set_column('L:L',10)
        sheet.set_column('M:M',18)
        sheet.set_column('N:N',40)
        sheet.set_column('O:O',40)
        sheet.set_column('P:P',30)
        sheet.set_column('Q:Q',15)
        sheet.set_column('R:R',40)
        
        """ SALIDAS - 1
        ID - 2
        GUÍA O FACTURA - 3
        CÓDIGO PRODUCTO - 4
        CENTRO DE COSTO - 5
        PRECIO - 6 """
        

        sheet.merge_range('A1:L1','REPORTE DE SALIDAS',title_format)
        sheet.write(1,0,"N°",header_format)
        sheet.write(1,1,"REFERENCIA",header_format)
        sheet.write(1,2,"GUÍA",header_format)
        sheet.write(1,3,"FACTURA",header_format)
        sheet.write(1,4,"CÓDIGO DE PRODUCTO",header_format)
        sheet.write(1,5,"PRODUCTO",header_format)
        sheet.write(1,6,"CÓDIGO C.C.",header_format)
        sheet.write(1,7,"CENTRO DE COSTO",header_format)
        sheet.write(1,8,"CANTIDAD",header_format)
        sheet.write(1,9,"UDM",header_format)
        sheet.write(1,10,"COSTO UNITARIO",header_format)
        sheet.write(1,11,"MONTO",header_format)
        sheet.write(1,12,"ORIGEN",header_format)
        sheet.write(1,13,"DESTINO",header_format)
        sheet.write(1,14,"SOLICITANTE",header_format)
        sheet.write(1,15,"CATEGORIA",header_format)
        sheet.write(1,16,"FECHA EFECTIVA",header_format)
        sheet.write(1,17,"NOTAS",header_format)
        
        row=2
        for data in picking:
            if data.state == 'done':
                for line in data.move_ids_without_package:
                    if line.state == 'cancel':
                        continue
                    
                    if data.location_id.usage == 'internal' and data.location_dest_id.usage == 'production':
                        sheet.write(row, 0, int(row - 2))
                        sheet.write(row, 1, data.name)
                        sheet.write(row, 2, data.guia or "")
                        sheet.write(row, 3, data.factura or "")
                        sheet.write(row, 4, line.product_id.default_code)
                        sheet.write(row, 5, line.product_id.name)
                        sheet.write(row, 6, "N/A")  #TODO: CENTER COST
                        sheet.write(row, 6, "N/A")  #TODO: CENTER COST
                        sheet.write(row, 8, line.quantity_done)
                        sheet.write(row, 9, line.product_id.uom_id.name)
                        sheet.write(row, 10, line.precio_unit_asiento)
                        sheet.write(row, 11, line.monto_asiento)
                        sheet.write(row, 12, data.location_id.display_name)
                        sheet.write(row, 13, data.location_dest_id.display_name)
                        sheet.write(row, 14, data.requester_id.name or "")
                        sheet.write(row, 15, line.product_id.categ_id.name or "")
                        sheet.write(row, 16, line.date or "",date_format)
                        note = html2plaintext(data.note).replace('\n','\r\n')
                        sheet.write(row, 17,note,saltolinea_format)
                        row += 1
                        
                    else:
                        if data.location_id.usage == 'production' and data.location_dest_id.usage == 'internal':
                            sheet.write(row, 0, int(row - 2))
                            sheet.write(row, 1, data.name)
                            sheet.write(row, 2, data.guia or "")
                            sheet.write(row, 3, data.factura or "")
                            sheet.write(row, 4, line.product_id.default_code)
                            sheet.write(row, 5, line.product_id.name)
                            sheet.write(row, 6, "N/A")  #TODO: CENTER COST
                            sheet.write(row, 6, "N/A")  #TODO: CENTER COST
                            sheet.write(row, 8, (line.quantity_done)*(-1))
                            sheet.write(row, 9, line.product_id.uom_id.name)
                            sheet.write(row, 10, line.precio_unit_asiento)
                            sheet.write(row, 11, line.monto_asiento)
                            sheet.write(row, 12, data.location_id.display_name)
                            sheet.write(row, 13, data.location_dest_id.display_name)
                            sheet.write(row, 14, data.requester_id.name or "")
                            sheet.write(row, 15, line.product_id.categ_id.name or "")
                            sheet.write(row, 16, line.date or "",date_format)
                            note = html2plaintext(data.note).replace('\n','\r\n')
                            sheet.write(row, 17,note,saltolinea_format)
                            row += 1