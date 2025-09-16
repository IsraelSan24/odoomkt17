from odoo import models, fields, api

_LOCATION = [
    ('uchucchacua', 'Uchucchacua'),
    ('tambomayo', 'Tambomayo'),
    ('orcopampa', 'Orcopampa'),
    ('taller', 'Taller'),
    ('yumpag', 'Yumpag')
]


class AnalyticAccountPartnerHistory(models.Model):
    _name = 'account.analytic.account.partner.history'
    _description = 'Historial de ubicaciones asignadas a centros de costo'

    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Centro de Costo',
        required=True,
        ondelete='cascade'
    )
    location_id = fields.Selection(
        selection=_LOCATION,
        string='Ubicación',
        required=True
    )
    start_datetime = fields.Datetime(
        string='Inicio de Asignación',
        required=True,
        default=fields.Datetime.now
    )
    end_datetime = fields.Datetime(string='Fin de Asignación')

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        fields = super(AnalyticAccountPartnerHistory, self).fields_get(allfields, attributes)
        if not self.env.user.has_group('module_name.group_partner_history_manager'):
            for field in ['start_datetime', 'end_datetime']:
                if field in fields:
                    fields[field]['readonly'] = True
        return fields
