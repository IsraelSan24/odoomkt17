from odoo import models, fields, _
import io as io
from io import BytesIO
from PIL import Image

class StockSummaryReport(models.TransientModel):
    _name = 'stock.summary.report'
    _description = 'Stock Summary Report'
    _inherit = ['report.formats']

    stock_location_ids = fields.Many2many(comodel_name="stock.location", compute="_get_query", string="Partner")


    def action_print_xlsx(self):
        return self.print_report_formats(function_name='xlsx', report_format='xlsx')


    def _get_file_name(self, function_name, file_name=False):
        dic_name = super(StockSummaryReport, self)._get_file_name(function_name, file_name=_("Stock Summary"))
        return dic_name


    def _get_datas_report_xlsx(self, workbook):
        ws = workbook.add_worksheet(_('Stock Summary'))

        style1 = {
            'font_color':'#3C839F',
            'align': 'center',
            'border': 1,
            'bold': True,
        }
        style2 = {
            'border': 1,
        }
        style3 = {
            'font_color':'#3C839F',
            'valign': 'vcenter',
            'align': 'center',
            'border': 1,
            'bold': True,
            'font_size': 12,
        }
        style4 = {
            'valign': 'vcenter',
            'border': 1,
            'font_size': 11,
            'num_format': 'dd/mm/yyyy',
        }

        stl1 = workbook.add_format(style1)
        stl2 = workbook.add_format(style2)
        stl3 = workbook.add_format(style3)
        stl4 = workbook.add_format(style4)

        ws.set_column('A:A', 50)
        ws.set_column('B:B', 13)
        ws.set_column('C:C', 16)
        ws.set_column('D:D', 10)
        ws.set_column('E:E', 20)
        ws.set_column('F:F', 15)
        ws.set_column('G:G', 13)
        ws.set_column('H:H', 11)
        ws.set_column('I:I', 22)

        ws.set_row(1,30)

        locations = ", ".join(self.stock_location_ids.mapped('name'))
        ws.merge_range('B2:E2', _('Locations: ') + locations, stl3)

        ws.write("A4:A4", _('PRODUCT'), stl1)
        ws.write("B4:B4", _('SERIE N°'), stl1)
        ws.write("C4:C4", _('CATEGORY'), stl1)
        ws.write("D4:D4", _('TYPE'), stl1)
        ws.write("E4:E4", _('UBICATION'), stl1)
        ws.write("F4:F4", _('ENTRIES'), stl1)
        ws.write("G4:G4", _('DEPARTURES'), stl1)
        ws.write("H4:H4", _('STOCK'), stl1)
        ws.write("I4:I4", _('EXPIRATION DATE'), stl1)
        ws.autofilter('A4:I4')

        records = self._get_query()
        row = 4
        for line in records:
            product_name = self.env['product.product'].search([('id','=',line['pp_id'])]).mapped('product_tmpl_id').name
            ws.write(row, 0, product_name, stl2)
            ws.write(row, 1, line['report_lot'], stl2)
            ws.write(row, 2, line['report_category'], stl2)
            ws.write(row, 3, line['report_product_type'], stl2)
            ws.write(row, 4, line['report_location'], stl2)
            ws.write(row, 5, line['report_incoming_qty'], stl2)
            ws.write(row, 6, line['report_outgoing_qty'], stl2)
            ws.write(row, 7, line['report_stock'], stl2)
            ws.write(row, 8, line['expiration_date'], stl4)
            row += 1


    def _get_query(self):
        self.stock_location_ids = [(6,0,self.env.user.stock_location_ids.ids)]
        where = "WHERE sl.id IN {}"
        query= """
            SELECT
                sq.id AS id,
                pp.id AS pp_id,
                pt.name AS report_product,
                spl.name AS report_lot,
                pc.name AS report_category,
                pt.detailed_type AS report_product_type,
                sl.name AS report_location,
                COALESCE((
                    SELECT SUM(sml.qty_done)
                    FROM stock_move AS sm
                    INNER JOIN stock_move_line AS sml ON sml.move_id = sm.id
                    WHERE sml.product_id = pp.id
                    AND sm.location_dest_id = sl.id
                    AND (sq.lot_id IS NULL OR sml.lot_id IS NULL OR sml.lot_id = sq.lot_id)
                    AND sml.qty_done > 0
                    AND sm.state = 'done'
                ), 0) AS report_incoming_qty,
                COALESCE((
                    SELECT SUM(sml.qty_done)
                    FROM stock_move AS sm
                    INNER JOIN stock_move_line AS sml ON sml.move_id = sm.id
                    WHERE sml.product_id = pp.id
                    AND sm.location_id = sl.id
                    AND (sq.lot_id IS NULL OR sml.lot_id IS NULL OR sml.lot_id = sq.lot_id)
                    AND sml.qty_done > 0
                    AND sm.state = 'done'
                ), 0) AS report_outgoing_qty,
                sq.quantity AS report_stock,
                spl.expiration_date AS expiration_date
            FROM stock_quant AS sq
            INNER JOIN product_product AS pp ON pp.id=sq.product_id
            INNER JOIN product_template AS pt ON pt.id = pp.product_tmpl_id
            INNER JOIN product_category AS pc ON pc.id = pt.categ_id
            INNER JOIN stock_location AS sl ON sl.id = sq.location_id
            LEFT JOIN stock_production_lot AS spl ON spl.id = sq.lot_id
            {}
            GROUP BY sq.id, pt.name, spl.name, pc.name, pt.detailed_type, sl.name, sq.quantity, pp.id, sl.id, spl.expiration_date
            ORDER BY pt.name
        """.format(where.format(tuple(self.stock_location_ids.ids)))
        self._cr.execute(query)
        res_query = self._cr.dictfetchall()
        return res_query