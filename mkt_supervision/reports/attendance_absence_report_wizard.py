
from odoo import models, fields, _
from datetime import datetime

class AttendanceAbsenceReport(models.TransientModel):
    _name = 'attendance.absence.report'
    _description = 'Attendance y Ausencias Mensual'
    _inherit = ['report.formats']  # heredamos para XLSX

    month = fields.Selection(
        [(str(i), str(i)) for i in range(1, 13)],
        string='Mes', required=True
    )
    year = fields.Char(
        string='Año', required=True,
        default=lambda self: str(datetime.now().year)
    )

    def action_print_xlsx(self):
        return self.print_report_formats(function_name='xlsx', report_format='xlsx')

    def _get_file_name(self, function_name, file_name=False):
        # Personalizamos el nombre del archivo resultante
        name = _('Reporte Asistencia Ausencia %s-%s') % (self.month, self.year)
        dic = super(AttendanceAbsenceReport, self)._get_file_name(
            function_name,
            file_name=name
        )
        return dic