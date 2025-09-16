from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountJournal(models.Model):
    _inherit = 'account.journal'
    
    journal_group_id = fields.Many2one(
        comodel_name='account.journal.group',
        string='Grupo de diarios'
    )
