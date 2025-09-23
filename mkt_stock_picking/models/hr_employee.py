from odoo import fields, models

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    driving_license_number = fields.Char(string="Número de licencia de conducir", size=10)
    partner_id = fields.Many2one(comodel_name='res.partner', string="Contact associated with the employee", domain=[('is_company', '=', False)])