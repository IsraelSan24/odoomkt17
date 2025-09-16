from odoo import _, api, fields, models
import logging

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'


    date_done = fields.Datetime(string="Date done", related="picking_id.date_done", store=True)