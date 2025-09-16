from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResCurrencyDayUpdate(models.TransientModel):
    _name = 'res.currency.day.update'
    _description = 'Res Currency Day Update'

    date = fields.Date(
        string='Fecha',
        default=fields.Date.today
    )

    @api.constrains('date')
    def constrain_date(self):
        for record in self:
            if record.date > fields.Date.today():
                raise ValidationError('Por favor seleccionar una fecha válida.')

    def action_update_day(self):
        res_curreny_model = self.env['res.currency'].action_currency_update(date=self.date)
        return