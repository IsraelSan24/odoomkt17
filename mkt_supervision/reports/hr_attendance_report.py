from odoo import _, models, fields
from datetime import datetime

class AttendanceReport(models.TransientModel):
    _name = 'attendance.report'
    _description = 'Attendance Report'
    _inherit = ['report.formats']

    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(string="End Date", required=True)

    def action_print_xlsx(self):
        return self.print_report_formats(function_name='xlsx', report_format='xlsx')

    def _get_file_name(self, function_name, file_name=False):
        dic_name = super(AttendanceReport, self)._get_file_name(function_name, file_name=_('Attendance Report'))
        return dic_name

    def _get_my_subordinates(self):
        my_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if not my_employee:
            return []

        subordinates = my_employee
        to_check = my_employee
        while to_check:
            children = self.env['hr.employee'].search([('parent_id', 'in', to_check.ids)])
            to_check = children - subordinates
            subordinates |= to_check

        return subordinates.ids

    def _get_datas_report_xlsx(self, workbook):
        ws = workbook.add_worksheet(_('Attendance Report'))

        ws.set_zoom(80)
        ws.set_column('A:A', 40)
        ws.set_column('B:B', 15)
        ws.set_column('C:C', 15)
        ws.set_column('D:D', 15)
        ws.set_column('E:E', 20)
        ws.set_column('F:F', 20)
        ws.set_column('G:G', 20)
        ws.set_column('H:H', 20)
        ws.set_column('I:I', 20)

        header_style = {
            'font_color': '#FFFFFF',
            'bg_color': '#000000',
            'align': 'center',
            'border': 2,
            'bold': True
        }
        data_style = {
            'font_color': '#000000',
            'bg_color': '#FFFFFF',
            'align': 'center',
            'border': 1
        }
        date_style = {
            'font_color': '#000000',
            'bg_color': '#FFFFFF',
            'align': 'center',
            'border': 1,
            'num_format': 'dd/mm/yyyy'
        }
        date_style2 = {
            'font_color': '#000000',
            'bg_color': '#FFFFFF',
            'align': 'center',
            'border': 1,
            'num_format': 'hh:mm:ss'
        }

        stl_header = workbook.add_format(header_style)
        stl_data = workbook.add_format(data_style)
        stl_date = workbook.add_format(date_style)
        stl_date2 = workbook.add_format(date_style2)

        ws.write('A1', _('Employee'), stl_header)
        ws.write('B1', _('Date'), stl_header)
        ws.write('C1', _('Check-in'), stl_header)
        ws.write('D1', _('Check-out'), stl_header)
        ws.write('E1', _('Check-in Latitude'), stl_header)
        ws.write('F1', _('Check-in Longitude'), stl_header)
        ws.write('G1', _('Check-out Latitude'), stl_header)
        ws.write('H1', _('Check-out Longitude'), stl_header)
        ws.write('I1', _('Within Allowed Area'), stl_header)

        records = self._get_query()
        row = 1

        for record in records:
            ws.write(row, 0, record['employee'], stl_data)
            ws.write(row, 1, record['date'], stl_date)
            ws.write(row, 2, record['check_in'], stl_date2)
            ws.write(row, 3, record['check_out'], stl_date2)
            ws.write(row, 4, record['check_in_latitude'], stl_data)
            ws.write(row, 5, record['check_in_longitude'], stl_data)
            ws.write(row, 6, record['check_out_latitude'], stl_data)
            ws.write(row, 7, record['check_out_longitude'], stl_data)
            ws.write(row, 8, 'Yes' if record['within_allowed_area'] else 'No', stl_data)
            row += 1

    def _get_query(self):
        subordinate_ids = self._get_my_subordinates()
        if not subordinate_ids:
            return []

        query = """
            WITH attendance_data AS (
                SELECT
                    at.employee_id,
                    (at.check_in AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')::date AS date,
                    MIN(at.check_in AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima') AS check_in,
                    MAX(at.check_out AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima') AS check_out,
                    BOOL_OR(at.within_allowed_area) AS within_allowed_area
                FROM hr_attendance at
                WHERE at.employee_id = ANY(%s)
                GROUP BY at.employee_id, (at.check_in AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')::date
            )
            SELECT
                rp.name AS employee,
                ad.date,
                ad.check_in::time AS check_in,
                ad.check_out::time AS check_out,
                ad.within_allowed_area,
                at_in.check_in_latitude,
                at_in.check_in_longitude,
                at_out.check_out_latitude,
                at_out.check_out_longitude
            FROM attendance_data ad
            JOIN hr_employee he ON he.id = ad.employee_id
            JOIN res_users ru ON ru.id = he.user_id
            JOIN res_partner rp ON rp.id = ru.partner_id
            LEFT JOIN hr_attendance at_in 
                ON at_in.employee_id = ad.employee_id 
                AND (at_in.check_in AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')::date = ad.date
                AND (at_in.check_in AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima') = ad.check_in
            LEFT JOIN hr_attendance at_out 
                ON at_out.employee_id = ad.employee_id 
                AND (at_out.check_out AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')::date = ad.date
                AND (at_out.check_out AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima') = ad.check_out
            ORDER BY ad.date DESC;
        """
        self._cr.execute(query, (subordinate_ids,))
        return self._cr.dictfetchall()
