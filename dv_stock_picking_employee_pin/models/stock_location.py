from odoo import models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    def get_warehouse(self):
        warehouse = self.env['stock.warehouse'].search(
            [
                '|',
                ('lot_stock_id', '=', self.id),
                ('wh_input_stock_loc_id', '=', self.id),
                ('wh_output_stock_loc_id', '=', self.id),
                ('wh_pack_stock_loc_id', '=', self.id),
                ('wh_qc_stock_loc_id', '=', self.id)
            ], limit=1
        )
        return warehouse
    
    def get_usage(self):
        return self.usage