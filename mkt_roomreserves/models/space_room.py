from odoo import models, fields

class SpaceRoom(models.Model):
    _name = 'space.room'
    _description = 'Space'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    floor = fields.Integer(string='Floor')
    capacity = fields.Integer(string='Capacity')
    active = fields.Boolean(string='Active', default=True)
    item_ids = fields.Many2many('space.booking.item', 'room_item_rel', 'room_id', 'item_id', string="Available Items")


    def action_open_rooms(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Salas',
            'res_model': 'space.room',
            'view_mode': 'kanban,tree,form',
            'domain': [('floor', '=', self.floor)],
            'context': {'default_floor': self.floor},
        }


    def action_view_reservations(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reservas',
            'res_model': 'space.booking',
            'view_mode': 'kanban,tree,form,calendar',
            'domain': [('room_id', '=', self.id)],
            'context': {'default_room_id': self.id},
        }