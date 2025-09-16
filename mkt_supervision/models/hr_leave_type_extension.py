from odoo import models, fields

class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    sigla = fields.Char(
        string='Sigla',
        size=5,
        help="Letra que representa esta ausencia en los reportes."
    )