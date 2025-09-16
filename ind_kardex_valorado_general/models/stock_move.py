from odoo import models,fields,api
from datetime import date
import logging
logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    asiento_id = fields.Integer(string="Id Asiento",compute="get_picking_id",store=True)
    monto_asiento = fields.Float(string="Monto del Asiento",compute="calcular_monto_asigned",store=True)
    precio_unit_asiento = fields.Float(string = "Precio Unitario Asientos" , compute="calcular_precio_unitario",store=True)


    @api.depends('account_move_ids')
    def get_picking_id(self):
        
        for record in self:
            if record.account_move_ids:
                primer_account_move=record.account_move_ids[0]
                record.asiento_id=primer_account_move.id

    @api.depends('account_move_ids')
    def calcular_monto_asigned(self):
        for record in self:
            asiento_monto = 0
            logger.warning("-----movimiento------")
            logger.warning(record)
            if record.location_dest_id.usage == 'internal':
                # Iteramos sobre todos los asientos vinculados al stock_move
                if record.account_move_ids:
                    logger.warning("------record----------")
                    for move in record.account_move_ids:
                        logger.warning("------move in rec-------")
                        logger.warning(move)
                        # Para cada asiento, revisamos sus líneas
                        if move.state=='posted':
                            for line in move.line_ids:
                                # Si la cuenta de la línea es una cuenta de inventario, sumamos el débito
                                if line.account_id.is_inventory_account:
                                    logger.warning(line.debit)
                                    logger.warning(line.credit)
                                    logger.warning("-----if-move in rec-account------")
                                    if line.debit==0:
                                        monto_add = line.credit*(-1)
                                    else:
                                        monto_add = line.debit
                                    
                                    asiento_monto +=monto_add

                            logger.warning("------end for------")
                            logger.warning(asiento_monto)
                record.monto_asiento = asiento_monto
                logger.warning("----if final-----")
                logger.warning(record.monto_asiento)

            else:
                logger.warning("-----else record--------")
                if record.account_move_ids:
                    logger.warning("-----else record-2-------")
                    for move in record.account_move_ids:
                        # Para cada asiento, revisamos sus líneas
                        if move.state=='posted':
                            for line in move.line_ids:
                                logger.warning("-----else line-----")
                                # Si la cuenta de la línea es una cuenta de inventario, sumamos el débito
                                if line.account_id.is_inventory_account:
                                    logger.warning(line.debit)
                                    logger.warning(line.credit)
                                    logger.warning("-----else-move in rec-account------")
                                    if line.debit==0:
                                        monto_add = line.credit
                                    else:
                                        monto_add = line.debit*(-1)
                                    
                                    asiento_monto +=monto_add
                            logger.warning("-----else-end for------")
                            logger.warning(asiento_monto)
                record.monto_asiento = asiento_monto
                logger.warning("----else final-----")
                logger.warning(record.monto_asiento)

    @api.depends('monto_asiento', 'product_uom_qty')
    def calcular_precio_unitario(self):
        for record in self:
            if record.monto_asiento and record.product_uom_qty:
                record.precio_unit_asiento=round(record.monto_asiento/record.product_uom_qty,6)
            else:
                record.precio_unit_asiento = 0