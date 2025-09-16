from odoo.tools.misc import xlsxwriter
from io import BytesIO


class ReportAgingExcel:
    def __init__(self, data):
        self.data = data

    def get_content(self, language: str):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # Formatos optimizados
        style_column = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'font_size': 10,
            'bold': True,
            'border': 1
        })
        style_content = workbook.add_format({
            'valign': 'vcenter',
            'font_size': 10,
            'border': 1
        })
        style_date = workbook.add_format({
            'font_size': 10,
            'num_format': 'dd/mm/yyyy',
            'align': 'center',
            'border': 1
        })

        # Configurar la hoja de cálculo
        ws = workbook.add_worksheet("Reporte de Anticuamiento")
        ws.set_column('A:A', 15)
        ws.set_column('B:B', 80)
        ws.set_column('C:C', 20)
        ws.set_column('D:D', 45)
        ws.set_column('E:E', 5)
        ws.set_column('F:F', 5)

        # Encabezados
        ws.write(0, 0, 'Código de Producto', style_column)
        ws.write(0, 1, 'Producto', style_column)
        ws.write(0, 2, 'Fecha', style_column)
        ws.write(0, 3, 'Referencia', style_column)
        ws.write(0, 4, 'Stock', style_column)

        # Escribir los datos
        for i, line in enumerate(self.data, start=1):
            ws.write(i, 0, line[3], style_content)
            ws.write(i, 1, line[2][language] if isinstance(line[2], dict) else line[2], style_content)
            ws.write(i, 2, line[1], style_date)
            ws.write(i, 3, line[0], style_content)
            ws.write(i, 4, line[5], style_content)

        workbook.close()
        output.seek(0)
        return output.read()
