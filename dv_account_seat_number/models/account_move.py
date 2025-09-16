from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError


class AccountMove(models.Model):
    _inherit = "account.move"
    # unique seat_number
    _sql_constraints = [
        ('unique_seat_number', 'unique (seat_number)',
         'El número de asiento ya existe!'),
    ]
    seat_number = fields.Char(string='Número de asiento', copy=False)

    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft=soft)
        self.compute_seat_number()
        return res

    def _get_journal_group_sequence(self):
        self.ensure_one()
        journal_group = self.journal_id.journal_group_id
        return journal_group.sequence_id

    def compute_seat_number(self):
        sorted_by_date = self.sorted(key=lambda r: r.date)
        for move in sorted_by_date:
            sequence = move._get_journal_group_sequence()
            if not move.seat_number and sequence:
                seat_number = sequence.with_context(
                    ir_sequence_date=move.date).next_by_id()
            else:
                seat_number = move.seat_number
            move.seat_number = seat_number
