from odoo import fields, models, api
from hashlib import blake2b


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_pin = fields.Char(
        string='Cód. validación',
        readonly=True
    )
    has_employee_pin = fields.Boolean(
        string='Cód. validación creado',
        readonly=True,
        default=False
    )
    employee_pin1 = fields.Char(
        size=6,
        string='Ingresar Cód. validación'
    )
    employee_pin2 = fields.Char(
        size=6,
        string='Repetir Cód. validación'
    )

    def change_employee_pin(self):
        self.has_employee_pin = False
        
    def save_employee_pin(self):
        for record in self:
            if not record.employee_pin:
                raise models.ValidationError(f'Los códigos de validación no coinciden. La contraseña debe ser de 6 dígitos.')
                
    @api.model_create_multi
    def create(self, vals):
        if vals.get('employee_pin1') and vals.get('employee_pin2') and vals.get('employee_pin1') == vals.get('employee_pin2') and len(vals.get('employee_pin1')) == 6:
            h = blake2b(digest_size=20)
            h.update(vals.get('employee_pin1').encode())
            vals['employee_pin'] = h.hexdigest()
            vals['has_employee_pin'] = True

        if vals.get('employee_pin1'):
            vals['employee_pin1'] = ''

        if vals.get('employee_pin2'):
            vals['employee_pin2'] = ''

        return super(HrEmployee, self).create(vals)

    
    def write(self, vals):
        if vals.get('employee_pin1') and vals.get('employee_pin2') and vals.get('employee_pin1') == vals.get('employee_pin2') and len(vals.get('employee_pin1')) == 6:
            h = blake2b(digest_size=15)
            h.update(vals.get('employee_pin1').encode())
            vals['employee_pin'] = h.hexdigest()
            vals['has_employee_pin'] = True

        if vals.get('employee_pin1'):
            vals['employee_pin1'] = ''

        if vals.get('employee_pin2'):
            vals['employee_pin2'] = ''

        return super(HrEmployee, self).write(vals)

