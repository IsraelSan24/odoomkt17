from odoo import models, fields
from odoo.tools.misc import xlsxwriter
from io import BytesIO
import base64
from datetime import datetime
from collections import defaultdict


class IndConsumptionAnalysis(models.TransientModel):
    _name = 'ind.consumption.analysis'
    _description = 'Consumption Analysis Report'

    date_from = fields.Date(
        string='Fecha inicio',
        required=True
    )
    date_to = fields.Date(
        string='Fecha fin',
        required=True
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company
    )
    file_data = fields.Binary(string='File')

    def generate_consumption_report(self):
        # Fetch product categories with no parents
        root_categories = self.env['product.category'].sudo().search([('parent_id', '=', False)])

        # Fetch stock moves based on location usage, date range, and state 'done'
        moves = self.env['stock.move'].sudo().search([
            '|',
            '&',
            ('location_id.usage', '=', 'internal'),
            ('location_dest_id.usage', '=', 'production'),
            '&',
            ('location_id.usage', '=', 'production'),
            ('location_dest_id.usage', '=', 'internal'),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', '=', self.company_id.id),
            ('state', '=', 'done'),  # Only include moves in state 'done'
        ])

        if not moves:
            raise ValueError('No se encontraron movimientos con el criterio determinado')

        # Prepare data grouped by category and center of cost
        category_data = {category.id: defaultdict(float) for category in root_categories}
        for move in moves:
            # Determine the category
            category = move.product_id.categ_id
            while category and category.parent_id:
                category = category.parent_id

            if category and category.id in category_data:
                center_name = 'N/A' #TODO: update in v17 center cost
                # Sum the amount based on location usage
                if move.location_id.usage == 'internal' and move.location_dest_id.usage == 'production':
                    category_data[category.id][center_name] += move.monto_asiento or 0.0
                elif move.location_id.usage == 'production' and move.location_dest_id.usage == 'internal':
                    category_data[category.id][center_name] -= move.monto_asiento or 0.0

        # Create Excel file
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        bold = workbook.add_format({'bold': True})

        for category in root_categories:
            center_costs = category_data.get(category.id, {})
            worksheet = workbook.add_worksheet(category.name[:31])  # Sheet names are limited to 31 characters

            # Write headers
            headers = ['Centro de Costo', 'Importe']
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, bold)

            # Set column widths
            worksheet.set_column(0, 0, 40)  # Set width of 'Centro de Costo' column
            worksheet.set_column(1, 1, 15)  # Set width of 'Importe' column

            # Write data and calculate total
            row = 1
            total_amount = 0.0
            for center_name, amount in center_costs.items():
                worksheet.write(row, 0, center_name)
                worksheet.write(row, 1, amount)
                total_amount += amount
                row += 1

            # Write total at the end
            worksheet.write(row, 0, 'Total', bold)
            worksheet.write(row, 1, total_amount, bold)

        workbook.close()

        # Encode the file and prepare for download
        result = base64.encodebytes(output.getvalue()).decode('utf-8')
        date_string = datetime.now().strftime('%Y-%m-%d')
        filename = f'Consumption_Analysis_Report_{date_string}.xlsx'

        self.write({'file_data': result})

        url = (
            f'web/content/?model={self._name}&id={self.id}&field=file_data'
            f'&download=true&filename={filename}'
        )

        return {
            'name': ('Consumption Analysis Report'),
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
