from odoo import fields, models


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'
    
    employee_pin = fields.Char(
        string='Cód. validación', 
        related='employee_id.employee_pin'
    )
    has_employee_pin = fields.Boolean(
        string='Cód. validación creado',
        related='employee_id.has_employee_pin'
    )
    employee_pin1 = fields.Char(
        string='Ingresar Cód. validación',
        related='employee_id.employee_pin1'
    )
    employee_pin2 = fields.Char(
        string='Repetir Cód. validación',
        related='employee_id.employee_pin2'
    )