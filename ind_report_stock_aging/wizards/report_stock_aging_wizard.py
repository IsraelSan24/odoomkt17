from odoo import models, fields
from odoo.exceptions import UserError
from ..reports.report_stock_aging_excel import ReportAgingExcel
import base64
import logging

_logger = logging.getLogger(__name__)


class StockAgingXlsx(models.TransientModel):
    _name = 'report.stock.aging.wizard'
    _description = 'Reporte Anticuamiento'
    
    file_data = fields.Binary(string='Archivo Excel', readonly=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        default=lambda self: self.env.company
    )
        
    def action_generate_report(self):
        try:
            query = '''
            SELECT DISTINCT ON (pp.id)
                sm.reference AS reference,
                sm.date AS move_date,
                pt.name as product_name,
                pp.default_code as pp_name,
                pp.id as product_id,
                sum(sq.quantity) as stock_on_hand
                -- (sq.quantity * svl.unit_cost) AS stock_value
            FROM 
                stock_move AS sm
            INNER JOIN 
                product_product AS pp ON sm.product_id = pp.id
            INNER JOIN 
                product_template AS pt ON pp.product_tmpl_id = pt.id
            LEFT JOIN
                stock_quant AS sq ON pp.id = sq.product_id
            INNER JOIN
                stock_location AS sl ON sq.location_id = sl.id
            WHERE 
                sm.state = 'done' 
                and sl.usage = 'internal'
                and sm.company_id = {}
            GROUP BY
                sm.reference, sm.date, pt.name, pp.default_code, pp.id
            ORDER BY
                pp.id, sm.date DESC;
            '''.format(self.company_id.id)

            self.env.cr.execute(query)
            result = self.env.cr.fetchall()
        except Exception as e:
            _logger.error(e)
            file_data = False
            raise UserError('Error al generar el archivo Excel: {}'.format(e))
        

        language = self.env.user.lang
        excel_file = ReportAgingExcel(result)
        file_data = base64.b64encode(excel_file.get_content(language)) 
        self.write({'file_data': file_data, 'company_id': self.company_id})

        return {
            'type': 'ir.actions.act_url',
            'url': "/web/content/?model=report.stock.aging.wizard&id={}&field=file_data&filename=reporte_anticuamiento&download=true".format(self.id),
            'target': 'self',
        }