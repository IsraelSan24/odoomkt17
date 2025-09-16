from odoo import fields, models


class Manufacturing(models.TransientModel):
    journal_group_id = fields.Many2one('account.journal.group', string='Grupo de diario')
    start_date = fields.Date(string='Fecha Inicial', required=True)
    finish_date = fields.Date(string='Fecha Final', required=True)
    
    def restart_seat_numbers(self):
        period_moves = self.env['account.move'].search([
            ('journal_id.journal_group_id', '=', self.journal_group_id.id),
            ('date', '>=', self.start_date),
            ('date', '<=', self.finish_date)
        ])
        period_moves.write({'seat_number':False})
        period_moves.compute_seat_number()
