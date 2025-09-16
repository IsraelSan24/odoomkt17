from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    detraction_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Cuenta de detracción',
        related='company_id.detraction_account_id', readonly=False,
        domain=lambda self: [('deprecated', '=', False)],
        help='Cuenta que será utilizada para registrar la deuda de detracciones.'
    )
