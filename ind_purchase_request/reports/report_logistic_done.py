from odoo import models
from datetime import timedelta

        
class PartnerDoneXlsx(models.AbstractModel):
    _name = 'report.ind_purchase_request.report_rfq_realizados'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Report Purchase Request Line Done Xlsx'

    def generate_xlsx_report(self, workbook, data, purchase_request_line):
        sheet = workbook.add_worksheet()
        
        # FORMATOS
        header_format_rfq=workbook.add_format({
            'bold':True,
            'bg_color': '#ffff00',
            'border':1,
            'font_size':12,
            'align':'center',
            'text_wrap': True,
        })
        header_format_oc=workbook.add_format({
            'bold':True,
            'bg_color':'#fabf8f',
            'border':1,
            'font_size':12,
            'align':'center',
            'text_wrap': True,
        })
        header_format_ing=workbook.add_format({
            'bold':True,
            'bg_color':'#92d050',
            'border':1,
            'font_size':12,
            'align':'center',
            'text_wrap': True, 
        })
        cell_format = workbook.add_format({
            'font_size':11,
            'align':'center',
            'text_wrap': True,
        })
        month_format=workbook.add_format({'num_format':'mmmm'})
        date_format=workbook.add_format({'num_format':'dd/mm/yy'})
        datetime_format=workbook.add_format({'num_format':'dd/mm/yy hh:mm:ss'})
        percentage_format = workbook.add_format({'num_format': '0%'})
                
        sheet.set_default_row(27)
        # ANCHO Y ALTO DE COLUMNAS Y FILAS
        sheet.set_row(0,34, workbook.add_format({'text_wrap': True}))
        sheet.set_row(1,17, workbook.add_format({'text_wrap': True}))
        sheet.set_column('A:A',11, cell_format)
        sheet.set_column('B:B',16, cell_format)
        sheet.set_column('C:C',14, cell_format)
        sheet.set_column('D:D',35, cell_format)
        sheet.set_column('E:E',12, cell_format)
        sheet.set_column('F:F',35, cell_format)
        sheet.set_column('G:G',17, cell_format)
        sheet.set_column('H:H',20, cell_format)
        sheet.set_column('I:I',14, cell_format)
        sheet.set_column('J:J',8, cell_format)
        sheet.set_column('K:K',8, cell_format)
        sheet.set_column('L:L',30, cell_format)
        sheet.set_column('M:M',30, cell_format)
        sheet.set_column('N:N',15, cell_format)
        sheet.set_column('O:O',9, cell_format)
        sheet.set_column('P:P',20, cell_format)
        sheet.set_column('Q:Q',16, cell_format)
        sheet.set_column('R:R',20, cell_format)
        sheet.set_column('S:S',20, cell_format)
        sheet.set_column('T:T',15, cell_format)
        sheet.set_column('U:U',28, cell_format)
        sheet.set_column('V:V',14, cell_format)
        sheet.set_column('W:W',28, cell_format)
        sheet.set_column('X:X',14, cell_format)
        sheet.set_column('Y:Y',9, cell_format)
        sheet.set_column('Z:Z',15, cell_format)
        sheet.set_column('AA:AA',12, cell_format)
        sheet.set_column('AB:AB',15, cell_format)
        sheet.set_column('AC:AC',6, cell_format)
        sheet.set_column('AD:AD',15, cell_format)
        sheet.set_column('AE:AE',10, cell_format)
        sheet.set_column('AF:AF',14, cell_format)
        sheet.set_column('AG:AG',14, cell_format)
        sheet.set_column('AH:AH',14, cell_format)
        sheet.set_column('AI:AI',8, cell_format)
        sheet.set_column('AJ:AJ',28, cell_format)
        sheet.set_column('AK:AK',20, cell_format)
        sheet.set_column('AL:AL',16, cell_format)
        sheet.set_column('AM:AM',13, cell_format)
        sheet.set_column('AN:AN',13, cell_format)
        
        # CABECERA
        sheet.merge_range('A1:L1','REQUERIMIENTOS',header_format_rfq)
        sheet.merge_range('M1:AG1','ORDEN DE COMPRA',header_format_oc)
        sheet.merge_range('AH1:AN1','INGRESO DE ALMACÉN',header_format_ing)
        
        # DATA RFQ
        encabezados_rfq = ["MES", "RQ", "ESTADO DE RQ", "SOLICITADO POR","FECHA DE CREACIÓN","APROBADOR","FECHA DE APROBACIÓN",
                       "PRODUCTO","CANTIDAD","UDM","CÓDIGO C.C.","CENTRO DE COSTO"]
        for i in range(len(encabezados_rfq)):
            sheet.write(1, i, encabezados_rfq[i], header_format_rfq)
        
        # DATA ORDEN DE COMPRA
        encabezados_oc = ["DESCRIPCIÓN DE ORDEN DE COMPRA", "CANTIDAD DE PRODUCTO ATENDIDO", "U/M OC", "OC",
                          "FECHA DE CREACIÓN", "CONDICIÓN DE OC", "ESTADO DE OC", "CREADO POR", "NOMBRE DE PROVEEDOR", "RUC", "PROVEEDOR SUGERIDO", "TIPO DE MONEDA", "TIPO DE CAMBIO",
                          "P/U SUBTOTAL PRODUCTO", "IGV DE PRODUCTO", "DESCUENTO(%) DE PRODUCTO", "IGV",
                          "IGV DE ORDEN DE COMPRA", "TOTAL INCL IGV", "EQUIVALENTE EN MONEDA", "CONDICIÓN DE PAGO OC"]
        for i in range(12,12+len(encabezados_oc)):
            sheet.write(1, i, encabezados_oc[i-12], header_format_oc)
        
        # DATA INGRESOS
        encabezados_ing = ["N° DE INGRESO", "CÓDIGO C.C.", "C.C. DE INGRESO", "FECHA Y HORA DE INGRESO", "CANTIDADES INGRESADAS", "U/M", "ESTADO DE INGRESO"]
        for i in range(33,33+len(encabezados_ing)):
            sheet.write(1, i, encabezados_ing[i-33], header_format_ing)

        row=2

        Lista_id =()
        Lista_mov_id =()
        print(Lista_id)

        for rfq_line in purchase_request_line:
            if rfq_line.purchase_lines:
                sheet.set_row(1,34, workbook.add_format({'text_wrap': True}))
                cont2=0    
                for purchase_line in rfq_line.purchase_lines:
                    cont1=0
                    if purchase_line.move_ids:
                        for mov in purchase_line.move_ids:
                            """ RFQ """
                            if mov.state in ['cancel']:
                                continue
                            sheet.write(row, 0, rfq_line.request_id.date_start, month_format)
                            sheet.write(row, 1, rfq_line.request_id.name or "")
                            if rfq_line.request_state == "draft":
                                sheet.write(row, 2, "BORRADOR")
                            elif rfq_line.request_state == "to_approve":
                                sheet.write(row, 2, "PARA SER APROBADO")
                            elif rfq_line.request_state == "approved":
                                sheet.write(row, 2, "APROBADO")
                            elif rfq_line.request_state == "done":
                                sheet.write(row, 2, "REALIZADO")
                            else:
                                sheet.write(row, 2, "")
                            sheet.write(row, 3, rfq_line.request_id.requested_by.name or "")
                            sheet.write(row, 4, rfq_line.request_id.date_start, date_format)
                            if rfq_line.approved_by.name:
                                sheet.write(row, 5, rfq_line.request_id.approved_by.name or "")
                            else:
                                sheet.write(row, 5, rfq_line.request_id.assigned_to.name or "")
                            if rfq_line.request_id.date_approved:
                                date_approved_local = rfq_line.request_id.date_approved - timedelta(hours=5)
                                sheet.write(row, 6, date_approved_local,datetime_format)
                            else:
                                sheet.write(row, 6, "")
                            sheet.write(row, 7, rfq_line.product_id.display_name or "")
                            """ sheet.write(row, 8, rfq_line.name or "") """
                            sheet.write(row, 8, rfq_line.product_qty or "")
                            """ if cont1==0 and cont2==0:
                                sheet.write(row, 8, rfq_line.product_qty) """
                            sheet.write(row, 9, rfq_line.product_uom_id.name or "")
                            sheet.write(row, 10, rfq_line.analytic_distribution or "") # code
                            sheet.write(row, 11, rfq_line.analytic_distribution or "") # name
                            sheet.write(row, 22, rfq_line.supplier_id.display_name or "")
                            
                            # ORDEN DE COMPRA
                            
                            if purchase_line.order_id.currency_id == purchase_line.order_id.company_id.currency_id:
                                monto_equivalente = round(purchase_line.price_total / purchase_line.order_id.inverse_rate, 3)
                            else:
                                monto_equivalente = round(purchase_line.price_total * purchase_line.order_id.inverse_rate, 3)
                            sheet.write(row, 12, purchase_line.name or "")
                            sheet.write(row, 13, purchase_line.product_qty or "")
                            """ if cont1==0:
                                if purchase_line.id in Lista_id:
                                    sheet.write(row,12,"")
                                else:    
                                    sheet.write(row, 12, purchase_line.product_qty) """
                            Lista_id=(*Lista_id, purchase_line.id)
                            sheet.write(row, 14, purchase_line.product_uom.name)
                            sheet.write(row, 15, purchase_line.order_id.name or "")
                            if purchase_line.order_id.date_approve:
                                date_approve_local = purchase_line.order_id.date_approve - timedelta(hours=5)
                                sheet.write(row, 16, date_approve_local,datetime_format)
                            if purchase_line.order_id.state  == "draft":
                                sheet.write(row, 17, "PETICIÓN DE PRESUPUESTO")
                            elif purchase_line.order_id.state  == "sent":
                                sheet.write(row, 17, "SOLICITUD DE PRESUPUESTO ENVIADO")
                            elif purchase_line.order_id.state  == "to_approve":
                                sheet.write(row, 17, "PARA APROBAR")
                            elif purchase_line.order_id.state  == "purchase":
                                sheet.write(row, 17, "ORDEN DE COMPRA")
                            elif purchase_line.order_id.state  == "done":
                                sheet.write(row, 17, "BLOQUEADO")
                            elif purchase_line.order_id.state  == "cancel":
                                sheet.write(row, 17, "CANCELADO")
                            else:   
                                sheet.write(row, 17, "NO TIENE OC")                               
                            if purchase_line.order_id.order_status == "almacen":
                                sheet.write(row, 18, "EN ALMACÉN")
                            elif purchase_line.order_id.order_status == "pago":
                                sheet.write(row, 18, "ÁREA DE PAGO")
                            elif purchase_line.order_id.order_status == "proveedor":
                                sheet.write(row, 18, "PROVEEDOR TRAE")
                            elif purchase_line.order_id.order_status == "regularización":
                                sheet.write(row, 18, "REGULARIZACIÓN")
                            elif purchase_line.order_id.order_status == "transporte":
                                sheet.write(row, 18, "ÁREA DE TRANSPORTE")
                            else:
                                sheet.write(row, 18, "")
                            sheet.write(row, 19, purchase_line.order_id.user_id.name or "")     
                            sheet.write(row, 20, purchase_line.order_id.partner_id.name or "")
                            sheet.write(row, 21, purchase_line.order_id.partner_id.vat or "")
                            sheet.write(row, 23, purchase_line.order_id.currency_id.name or "")
                            sheet.write(row, 24, purchase_line.order_id.inverse_rate or "")
                            sheet.write(row, 25, purchase_line.price_subtotal)
                            sheet.write(row, 26, purchase_line.price_tax)
                            sheet.write(row, 27, purchase_line.discount / 100 or 0, percentage_format)
                            u = ', '.join(purchase_line.taxes_id.mapped('name'))
                            if u == "18%":
                                sheet.write(row, 28, 0.18, percentage_format)
                                sheet.write(row, 29, "ADICIONAL")
                            elif u == "18% incluido":
                                sheet.write(row, 28, 0.18, percentage_format)
                                sheet.write(row, 29, "INCLUIDO")
                            elif u == "18% (Included in price)":
                                sheet.write(row, 28, 0.18, percentage_format)
                                sheet.write(row, 29, "INCLUIDO EN PRECIO")
                            elif u == "0% Exonerated":
                                sheet.write(row, 28, 0, percentage_format)
                                sheet.write(row, 29, "EXONERADO")
                            else:
                                sheet.write(row, 28, "")
                                sheet.write(row, 29, "")
                            sheet.write(row, 30, purchase_line.price_total)
                            sheet.write(row, 31, monto_equivalente)
                            sheet.write(row, 32, purchase_line.order_id.payment_term_id.name or "")
                             
                            # INGRESOS
                            if mov.state=='done':
                                sheet.write(row, 33, mov.reference)
                                sheet.write(row, 34, mov.analytic_distribution or "") # code
                                sheet.write(row, 35, mov.analytic_distribution or "") # name
                                if mov.date:
                                    move_date = mov.date - timedelta(hours=5)
                                    sheet.write(row, 36, move_date ,datetime_format)
                                else:
                                    sheet.write(row, 37, "")
                                if mov.id in Lista_mov_id:
                                    sheet.write(row, 37, mov.product_uom_qty)
                                    sheet.write(row, 38, mov.product_uom.name)
                                else:
                                    sheet.write(row, 37, mov.product_uom_qty)
                                    sheet.write(row, 38, mov.product_uom.name)
                                    """ sheet.write(row, 27, mov.product_uom.name) """
                                    """ if mov.location_dest_id.usage=='internal':
                                        sheet.write(row, 37, 'Ingreso')
                                    else:
                                        sheet.write(row, 37, 'Salida') """
                                sheet.write(row, 39, "REALIZADO")
                                Lista_mov_id=(*Lista_mov_id,mov.id)
                                """ sheet.write(row, 27, mov.picking_id.date_done,date_format) """
                            else:
                                sheet.write(row, 33, "")
                                sheet.write(row, 34, "")
                                sheet.write(row, 35, "")
                                sheet.write(row, 36, "")
                                sheet.write(row, 37, "")
                                sheet.write(row, 38, "")
                                sheet.write(row, 39, "EN PROCESO")

                            row += 1
                            cont1 +=1
                    else:
                    # RFQ
                        sheet.write(row, 0, rfq_line.request_id.date_start, month_format)
                        sheet.write(row, 1, rfq_line.request_id.name or "")
                        if rfq_line.request_state == "draft":
                            sheet.write(row, 2, "BORRADOR")
                        elif rfq_line.request_state == "to_approve":
                            sheet.write(row, 2, "PARA SER APROBADO")
                        elif rfq_line.request_state == "approved":
                            sheet.write(row, 2, "APROBADO")
                        elif rfq_line.request_state == "rejected":
                            sheet.write(row, 2, "RECHAZADO")
                        elif rfq_line.request_state == "done":
                            sheet.write(row, 2, "REALIZADO")
                        else:
                            sheet.write(row, 2, "")
                        sheet.write(row, 3, rfq_line.request_id.requested_by.name or "")
                        sheet.write(row, 4, rfq_line.request_id.date_start, date_format)
                        if rfq_line.approved_by.name:
                            sheet.write(row, 5, rfq_line.request_id.approved_by.name or "")
                        else:
                            sheet.write(row, 5, rfq_line.request_id.assigned_to.name or "")
                        if rfq_line.request_id.date_approved:
                            date_approved_local = rfq_line.request_id.date_approved - timedelta(hours=5)
                            sheet.write(row, 6, date_approved_local,datetime_format)
                        else:
                            sheet.write(row, 6, "")
                        sheet.write(row, 7, rfq_line.product_id.display_name or "")
                        """ sheet.write(row, 8, rfq_line.name or "") """
                        sheet.write(row, 8, rfq_line.product_qty)
                        sheet.write(row, 9, rfq_line.product_uom_id.name or "")
                        sheet.write(row, 10, rfq_line.analytic_distribution or "") # code
                        sheet.write(row, 11, rfq_line.analytic_distribution or "") # name
                        sheet.write(row, 22, rfq_line.supplier_id.display_name or "")
                                
                        # ORDEN DE COMPRA
                        if purchase_line.order_id.currency_id == purchase_line.order_id.company_id.currency_id:
                                monto_equivalente = round(purchase_line.price_total / purchase_line.order_id.inverse_rate, 3)
                        else:
                            monto_equivalente = round(purchase_line.price_total * purchase_line.order_id.inverse_rate, 3)
                        sheet.write(row, 12, purchase_line.name or "")
                        sheet.write(row, 13, purchase_line.product_qty or "")
                        """ if cont1==0:
                            if purchase_line.id in Lista_id:
                                sheet.write(row,12,"")
                            else:    
                                sheet.write(row, 12, purchase_line.product_qty) """
                        Lista_id=(*Lista_id, purchase_line.id)
                        sheet.write(row, 14, purchase_line.product_uom.name)
                        sheet.write(row, 15, purchase_line.order_id.name or "")
                        if purchase_line.order_id.date_approve:
                            date_approve_local = purchase_line.order_id.date_approve - timedelta(hours=5)
                            sheet.write(row, 16, date_approve_local,datetime_format)
                        if purchase_line.order_id.state  == "draft":
                            sheet.write(row, 17, "PETICIÓN DE PRESUPUESTO")
                        elif purchase_line.order_id.state  == "sent":
                            sheet.write(row, 17, "SOLICITUD DE PRESUPUESTO ENVIADO")
                        elif purchase_line.order_id.state  == "to_approve":
                            sheet.write(row, 17, "PARA APROBAR")
                        elif purchase_line.order_id.state  == "purchase":
                            sheet.write(row, 17, "ORDEN DE COMPRA")
                        elif purchase_line.order_id.state  == "done":
                            sheet.write(row, 17, "BLOQUEADO")
                        elif purchase_line.order_id.state  == "cancel":
                            sheet.write(row, 17, "CANCELADO")
                        else:   
                            sheet.write(row, 17, "NO TIENE OC")                               
                        if purchase_line.order_id.order_status == "almacen":
                            sheet.write(row, 18, "EN ALMACÉN")
                        elif purchase_line.order_id.order_status == "pago":
                            sheet.write(row, 18, "ÁREA DE PAGO")
                        elif purchase_line.order_id.order_status == "proveedor":
                            sheet.write(row, 18, "PROVEEDOR TRAE")
                        elif purchase_line.order_id.order_status == "regularización":
                            sheet.write(row, 18, "REGULARIZACIÓN")
                        elif purchase_line.order_id.order_status == "transporte":
                            sheet.write(row, 18, "ÁREA DE TRANSPORTE")
                        else:
                            sheet.write(row, 18, "")
                        sheet.write(row, 19, purchase_line.order_id.user_id.name or "")     
                        sheet.write(row, 20, purchase_line.order_id.partner_id.name or "")
                        sheet.write(row, 21, purchase_line.order_id.partner_id.vat or "")
                        sheet.write(row, 23, purchase_line.order_id.currency_id.name or "")
                        sheet.write(row, 24, purchase_line.order_id.inverse_rate or "")
                        sheet.write(row, 25, purchase_line.price_subtotal)
                        sheet.write(row, 26, purchase_line.price_tax)
                        sheet.write(row, 27, purchase_line.discount / 100 or 0, percentage_format)
                        u = ', '.join(purchase_line.taxes_id.mapped('name'))
                        if u == "18%":
                            sheet.write(row, 28, 0.18, percentage_format)
                            sheet.write(row, 29, "ADICIONAL")
                        elif u == "18% incluido":
                            sheet.write(row, 28, 0.18, percentage_format)
                            sheet.write(row, 29, "INCLUIDO")
                        elif u == "18% (Included in price)":
                            sheet.write(row, 28, 0.18, percentage_format)
                            sheet.write(row, 29, "INCLUIDO EN PRECIO")
                        elif u == "0% Exonerated":
                            sheet.write(row, 28, 0, percentage_format)
                            sheet.write(row, 29, "EXONERADO")
                        else:
                            sheet.write(row, 28, "")
                            sheet.write(row, 29, "")
                        sheet.write(row, 30, purchase_line.price_total)
                        sheet.write(row, 31, monto_equivalente)
                        sheet.write(row, 32, purchase_line.order_id.payment_term_id.name or "")
                        
                        # INGRESOS
                        sheet.write(row, 33, "")
                        sheet.write(row, 34, "")
                        sheet.write(row, 35, "")
                        sheet.write(row, 36, "")
                        sheet.write(row, 37, "")
                        sheet.write(row, 38, "")
                        sheet.write(row, 39, "") 

                        row += 1
                    # Añadir una fila en blanco entre objetos
                    # row+=1  
            else:
            # RFQ
                sheet.write(row, 0, rfq_line.request_id.date_start, month_format)
                sheet.write(row, 1, rfq_line.request_id.name or "")
                if rfq_line.request_state == "draft":
                    sheet.write(row, 2, "BORRADOR")
                elif rfq_line.request_state == "to_approve":
                    sheet.write(row, 2, "PARA SER APROBADO")
                elif rfq_line.request_state == "approved":
                    sheet.write(row, 2, "APROBADO")
                elif rfq_line.request_state == "rejected":
                    sheet.write(row, 2, "RECHAZADO")
                elif rfq_line.request_state == "done":
                    sheet.write(row, 2, "REALIZADO")
                else:
                    sheet.write(row, 2, "")
                sheet.write(row, 3, rfq_line.request_id.requested_by.name or "")
                sheet.write(row, 4, rfq_line.request_id.date_start, date_format)
                if rfq_line.approved_by.name:
                    sheet.write(row, 5, rfq_line.request_id.approved_by.name or "")
                else:
                    sheet.write(row, 5, rfq_line.request_id.assigned_to.name or "")
                if rfq_line.request_id.date_approved:
                    date_approved_local = rfq_line.request_id.date_approved - timedelta(hours=5)
                    sheet.write(row, 6, date_approved_local,datetime_format)
                else:
                    sheet.write(row, 6, "")
                sheet.write(row, 7, rfq_line.product_id.display_name or "")
                """ sheet.write(row, 8, rfq_line.name or "") """
                sheet.write(row, 8, rfq_line.product_qty)
                sheet.write(row, 9, rfq_line.product_uom_id.name or "")
                sheet.write(row, 10, rfq_line.analytic_distribution or "") # code
                sheet.write(row, 11, rfq_line.analytic_distribution or "") # name
                sheet.write(row, 22, rfq_line.supplier_id.display_name or "")
                        
                # ORDEN DE COMPRA
                sheet.write(row, 12, "")
                sheet.write(row, 13, "")
                sheet.write(row, 14, "")
                sheet.write(row, 15, "")
                sheet.write(row, 16, "")
                sheet.write(row, 17, "NO TIENE OC")        
                sheet.write(row, 18, "")
                sheet.write(row, 19, "")
                sheet.write(row, 20, "")
                sheet.write(row, 22, "")
                sheet.write(row, 23, "")
                sheet.write(row, 24, "")
                sheet.write(row, 25, "")
                sheet.write(row, 26, "")
                sheet.write(row, 27, "")
                sheet.write(row, 28, "")
                sheet.write(row, 29, "")
                sheet.write(row, 30, "")
                sheet.write(row, 31, "") 
                sheet.write(row, 32, "")
                
                # INGRESOS                
                sheet.write(row, 33, "")
                sheet.write(row, 34, "")
                sheet.write(row, 35, "")
                sheet.write(row, 36, "")
                sheet.write(row, 37, "")
                sheet.write(row, 38, "")
                sheet.write(row, 39, "") 

                row += 1
            # Añadir una fila en blanco entre objetos
            # row+=1