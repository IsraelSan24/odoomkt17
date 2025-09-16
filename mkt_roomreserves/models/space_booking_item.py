from odoo import models, fields

class SpaceBookingItem(models.Model):
    _name = 'space.booking.item'
    _description = 'Reserve Item'

    name = fields.Char(string='Item', required=True)
    stock = fields.Integer(string='Stock', store=True)
    room_ids = fields.Many2many(
        'space.room', 
        'room_item_rel',  # Nombre de la tabla intermedia
        'item_id',         # Campo que hace referencia a space.booking.item
        'room_id',         # Campo que hace referencia a space.room
        string="Rooms"
    )
