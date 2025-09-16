from odoo import _, api, fields, models, tools

class StockSummaryOut(models.Model):
    _name = 'stock.summary.out'
    _description = 'Stock summary out'
    _auto = False

    assigned_location_ids = fields.Many2many(comodel_name='stock.location', compute='compute_assigned_location')
    date_done = fields.Datetime(string="Date")
    reference = fields.Char(string="Reference")
    product = fields.Char(string="Product")
    product_id = fields.Many2one(comodel_name='product.product', string="product_id")
    product_default_code = fields.Char(string="Product Default Code", related="product_id.default_code")
    location = fields.Char(string="Source Locatio")
    location_id = fields.Many2one(comodel_name='stock.location', string="location_id")
    location_dest = fields.Char(string="Destination Location")
    location_dest_id = fields.Many2one(comodel_name='stock.location', string="location_dest_id")
    product_uom_qty = fields.Float(string="Demand")
    product_uom = fields.Many2one(comodel_name='uom.uom', string="product_uom")
    state = fields.Selection([
        ('draft', 'New'), ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Move'),
        ('confirmed', 'Waiting Availability'),
        ('partially_available', 'Partially Available'),
        ('assigned', 'Available'),
        ('done', 'Done')], string="Status")


    def compute_assigned_location(self):
        self.assigned_location_ids = [(6,0,self.env.user.stock_location_ids.ids)]


    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW %s AS (
            %s
            FROM %s AS sm
            %s
            )""" %(self._table, self._select(), self._from(), self._join()))


    def _select(self):
        select = """
            SELECT
                sm.id AS id,
                sm.date_done AS date_done,
                sm.reference AS reference,
                pt.name AS product,
                pp.default_code AS product_default_code,
                sm.product_id AS product_id,
                sl.name AS location,
                sm.location_id AS location_id,
                sl2.name AS location_dest,
                sm.location_dest_id AS location_dest_id,
                sm.product_uom_qty AS product_uom_qty,
                sm.product_uom AS product_uom,
                sm.state AS state
        """
        return select


    def _from(self):
        return 'stock_move'


    def _join(self):
        join = """
                LEFT JOIN product_product AS pp ON sm.product_id=pp.id
                LEFT JOIN product_template AS pt ON pp.product_tmpl_id=pt.id
                LEFT JOIN stock_location AS sl ON sm.location_id=sl.id
                LEFT JOIN stock_location AS sl2 ON sm.location_dest_id=sl2.id
            WHERE pp.active = TRUE AND pt.active = TRUE
        """
        return join