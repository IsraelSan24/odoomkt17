from odoo import models


class ReportParentProductXlsx(models.AbstractModel):
    _name = 'report.ind_parent_product.report_alternatives_products'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Report Parent Product Xlsx'

    def generate_xlsx_report(self, workbook, data, parent_products):
        sheet = workbook.add_worksheet()
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': 'grey',
            'border': 1,
            'font_size': 12,
            'align': 'center',
            'color': 'white',
        })
        title_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 16
        })
        center_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter'
        })
        
        sheet.set_column('A:A',10,center_format)
        sheet.set_column(1,1,40)
        sheet.set_column('C:C',40)
        sheet.merge_range('A1:C1','Relacion de P. Originales con Alternativos',title_format)
        sheet.write(2,0,"N°",header_format)
        sheet.write(2,1,"P. Original",header_format)
        sheet.write(2,2,"P. Alterntivo",header_format)

        row=3

        for record in parent_products:
            for rec in record.product_alternativos:
                sheet.write(row,0,int(row-2))
                sheet.write(row,1,record.product_name)
                sheet.write(row,2,rec.name)
                row+=1
        row+=1
