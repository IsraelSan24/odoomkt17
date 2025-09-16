from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    last_attendance_id = fields.Many2one(
        'hr.attendance',
        string='Última asistencia',
        compute='_compute_last_attendance_id',  # se mantiene igual que Odoo core
        store=True,
        groups=(
            'hr_attendance.group_hr_attendance_user,'
            'hr_attendance.group_hr_attendance_manager,'
            'hr_attendance.group_hr_attendance,'
            'mkt_supervision.group_supervision_supervisor,'
            'mkt_supervision.group_supervision_admin'
        ),
    )