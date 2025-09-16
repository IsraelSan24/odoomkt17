from odoo import fields, models
from hashlib import blake2b


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    requester_pin = fields.Char(string='Cód. validación')
    requester_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Solicitante'
    )
    is_form_validate = fields.Boolean(
        string='Formulario validado',
        default=False
    )
    
    def action_confirm(self):
        res = super(StockPicking, self).action_confirm()
        self.validate_requester_pin()
        return res

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        self.validate_requester_pin()
        return res

    def validate_requester_pin(self):
        for record in self.filtered(lambda sp: sp.picking_type_id.code == 'internal'):
            if (record.location_id.get_warehouse() == record.location_dest_id.get_warehouse() and 
                record.location_id.get_usage() == record.location_dest_id.get_usage()):
                continue  # Salta la validación si es una transferencia dentro del mismo almacén

            if record.requester_id and record.requester_pin:
                employee_pin = record.requester_id.employee_pin
                h = blake2b(digest_size=15)
                h.update(record.requester_pin.encode())
                if h.hexdigest() == employee_pin:
                    record.write({'is_form_validate': True,
                                  'requester_pin': ''})
                else:
                    raise models.ValidationError(
                        f'El código de validación no coincide con el solicitante.')
            elif not record.is_form_validate and record.requester_id and not record.requester_pin:
                raise models.ValidationError(
                    f'Especifique el código de validación del solicitante.')
            elif not record.is_form_validate and record.requester_pin and not record.requester_id:
                raise models.ValidationError(f'Especifique el solicitante.')
            elif not record.is_form_validate and not record.requester_pin and not record.requester_id:
                raise models.ValidationError(
                    f'Especifique el solicitante y su código de validación.')
    