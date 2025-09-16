from odoo import fields, models, api


class DetractionTable(models.Model):
    _name = 'l10n_pe_detraction.table'
    _description = 'Tabla de detracciones'
    _sql_constraints = [
        ('code_annex_number_uniq', 'unique (code,annex_number)',
         'El código debe ser único por anexo')
    ]

    name = fields.Char(
        string='Nombre',
        required=True
    )
    code = fields.Char(
        string='Código',
        required=True
    )
    annex_number = fields.Selection(
        string='Anexo',
        required=True,
        selection=[
            ('annex_one', 'Anexo I'),
            ('annex_two', 'Anexo II'),
            ('annex_three', 'Anexo III'),
        ]
    )
    percent = fields.Float(string='Porcentaje')

    @api.depends(lambda self: (self._rec_name,) if self._rec_name else ())
    def _compute_display_name(self):
        for table in self:
            table.display_name = f'{table.code} {table.name}'
