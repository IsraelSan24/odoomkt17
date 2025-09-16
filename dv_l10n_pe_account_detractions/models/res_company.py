from odoo import _, api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    detraction_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Cuenta de detracción',
        domain=lambda self: [('deprecated', '=', False)],
        help='Cuenta que será utilizada para registrar la deuda de detracciones.'
    )
