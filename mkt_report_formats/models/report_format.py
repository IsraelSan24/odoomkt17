from odoo import api, fields, models, _
from io import BytesIO
import xlsxwriter

class ReportFormats(models.Model):
    _name = 'report.formats'
    _description = 'Report Formats xls, txt'

    from_object = fields.Char()

    def print_report_formats(self, function_name='xlsx', report_format='xlsx'):
        return {
            'type': 'ir.actions.act_url',
            'url': 'reports/type_format/{}/{}/{}/{}'.format(self._name, function_name, report_format, self.id),
            'target':'new',
        }
    
    def document_print(self, function_name=False):
        output = BytesIO()
        output = self._init_buffer(output, function_name)
        output.seek(0)
        return output.read()
    
    def file_name(self, file_format, function_name=False):
        name = "%s.%s" % (self._get_file_name(function_name).get(function_name), file_format)
        return name
    
    
    def _get_file_name(self, function_name, file_name=False):
        dic = {
            function_name: file_name or self._name
        }
        return dic
    

    def _generate_xlsx(self, output, function_name):
        workbook = xlsxwriter.Workbook(output)
        content = getattr(self, "_get_datas_report_%s" % function_name)(workbook)
        workbook.close()


    def _get_datas_report_xlsx(self, workbook):
        ws = workbook.add_worksheet('world')
        ws.write("A1:D1", "Hello World")


    def _generate_txt(self, output, function_name):
        content = getattr(self, "_get_datas_report_%s" % function_name)(output)
        output.write(content.encode())


    def _get_datas_report_txt(self, output):
        content = ""
        for x in range(0, 10):
            content += "Hola mundo %s\n" %x
        return content


    def _init_buffer(self, output, function_name='xlsx'):
        getattr(self, '_generate_%s' % (function_name or ''))(output, function_name)
        return output