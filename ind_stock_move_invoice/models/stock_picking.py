from odoo import fields, models, _
from odoo.exceptions import UserError
import logging
logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    account_move_ids = fields.Many2many(
        comodel_name='account.move',
        relation='account_move_stock_picking_rel',
        column1='stock_picking_id',
        column2='account_move_id',
        string='Factura',
        readonly=True
    )

    # OVERRIDE MODULE STOCK_MOVE_INVOICE
    def action_create_bill(self):
        """This is the function for creating vendor bill from the picking"""
        for picking_id in self:
            current_user = self.env.uid

            if picking_id.picking_type_id.code == 'incoming':
                vendor_journal_id = picking_id.env['ir.config_parameter'].sudo().get_param(
                    'stock_move_invoice.vendor_journal_id') or False

                if not vendor_journal_id:
                    raise UserError(_("Please configure the journal from the settings."))
    
                invoice_line_list = []

                for move_ids_without_package in picking_id.move_ids_without_package:
                    #  START OVERRIDE
                    if move_ids_without_package.account_move_line_ids:
                        total_quantity = sum(line.quantity for line in move_ids_without_package.account_move_line_ids.filtered(lambda x: x.parent_state == 'posted'))
                        outstanding_quantity = move_ids_without_package.quantity - total_quantity
                    else:                       
                        outstanding_quantity = move_ids_without_package.quantity
                    if outstanding_quantity > 0:
                        vals = (0, 0, {
                            'name': move_ids_without_package.description_picking,
                            'product_id': move_ids_without_package.product_id.id,
                            'price_unit': move_ids_without_package.purchase_line_id.price_unit,
                            'analytic_distribution': move_ids_without_package.purchase_line_id.analytic_distribution,
                            'product_uom_id': move_ids_without_package.purchase_line_id.product_uom.id,
                            'account_id': move_ids_without_package.product_id.property_account_expense_id.id if move_ids_without_package.product_id.property_account_expense_id
                            else move_ids_without_package.product_id.categ_id.property_account_expense_categ_id.id,
                            'tax_ids': [(6, 0, [picking_id.company_id.account_purchase_tax_id.id])],
                            'discount': move_ids_without_package.purchase_line_id.discount,
                            'tax_ids': [(6, 0, move_ids_without_package.purchase_line_id.taxes_id.ids or [])],
                            'quantity': outstanding_quantity,
                            'purchase_line_id': move_ids_without_package.purchase_line_id.id,
                            'stock_move_id': move_ids_without_package.id
                        })
                        invoice_line_list.append(vals)
                    #  END OVERRIDE

                journal = picking_id.env['account.journal'].search([
                    ('default_compra', '=', True),
                    ('company_id', '=', picking_id.company_id.id)
                ], limit=1)

                if not journal:
                    raise UserError(_("No se encontró un Diario con 'Compra' activo para la compañía %s") % picking_id.company_id.display_name)

                invoice = picking_id.env['account.move'].create({
                    'move_type': 'in_invoice',
                    'invoice_origin': picking_id.name,
                    'invoice_user_id': current_user,
                    'narration': picking_id.name,
                    'partner_id': picking_id.partner_id.id,
                    'currency_id': picking_id.purchase_id.currency_id.id,  #OVERRIDE PARA TOMAR LA MONEDA DEL MOVIMIENTO
                    'journal_id': journal.id,
                    'payment_reference': picking_id.name,
                    'picking_id': picking_id.id,
                    'invoice_line_ids': invoice_line_list,
                    'transfer_ids': self,
                    'invoice_payment_term_id':picking_id.purchase_id.payment_term_id.id  # OVERRIDE PARA JALAR LAS CONDICIONES DE PAGO
                })
                #  START OVERRIDE
                for line in invoice.line_ids:
                    if line.account_id.account_type == 'payable':  # Ejemplo: modificar solo cuentas por pagar
                        transfer_details=[]
                        for transfer in invoice.transfer_ids:
                            purchase_name = transfer.origin if transfer.origin else "Sin pedido de compra"
                            transfer_details.append(f"{transfer.name} {purchase_name}")
                        transfer_names = ', '.join(transfer_details)
                        line.name = f"{transfer_names}"
                return invoice
                #  END OVERRIDE

    #  OVERRIDE MODULE STOCK MOVE INVOICE
    def action_create_multi_invoice_for_multi_transfer(self):
        picking_type = list(self.picking_type_id)
        #  START OVERRIDE
        picking_ids = list(self)
        if all(first.state=='done' for first in picking_ids):
            if all(first.code == 'outgoing' for first in picking_type):
        #  END OVERRIDE
                partner = list(self.partner_id)
                if all(first == partner[0] for first in partner):
                    partner_id = self.partner_id
                    invoice_line_list = []
                    customer_journal_id = \
                        self.env['ir.config_parameter'].sudo().\
                            get_param('stock_move_invoice.customer_journal_id') \
                        or False
                    if not customer_journal_id:
                        raise UserError(
                            _("Please configure the journal from settings"))
                    for picking_id in self:
                        for move_ids_without_package in picking_id.move_ids_without_package:
                            #  START OVERRIDE
                            if move_ids_without_package.state=='done':
                                if move_ids_without_package.account_move_line_ids:
                                    total_quantity = sum(line.quantity for line in move_ids_without_package.account_move_line_ids.filtered(lambda x: x.parent_state == 'posted'))
                                    outstanding_quantity = move_ids_without_package.quantity - total_quantity
                                else:
                                    outstanding_quantity = move_ids_without_package.quantity
                                if outstanding_quantity > 0:
                            #  END OVERRIDE
                                    vals = (0, 0, {
                                        'name': move_ids_without_package.description_picking,
                                        'product_id': move_ids_without_package.product_id.id,
                                        'price_unit': move_ids_without_package.purchase_line_id.price_unit,
                                        'analytic_distribution': move_ids_without_package.purchase_line_id.analytic_distribution,
                                        'product_uom_id': move_ids_without_package.purchase_line_id.product_uom.id,
                                        'account_id': move_ids_without_package.product_id.property_account_expense_id.id if move_ids_without_package.product_id.property_account_expense_id
                                        else move_ids_without_package.product_id.categ_id.property_account_expense_categ_id.id,
                                        'discount': move_ids_without_package.purchase_line_id.discount,
                                        'tax_ids': [(6, 0, move_ids_without_package.purchase_line_id.taxes_id.ids or [])],
                                        'quantity': outstanding_quantity,
                                        'purchase_line_id': move_ids_without_package.purchase_line_id.id,
                                        'stock_move_id': move_ids_without_package.id
                                    })
                                    invoice_line_list.append(vals)
                    invoice = self.env['account.move'].create({
                        'move_type': 'out_invoice',
                        'invoice_origin': picking_id.name,
                        'invoice_user_id': self.env.uid,
                        'narration': picking_id.name,
                        'partner_id': partner_id.id,
                        'currency_id': picking_id.purchase_id.currency_id.id,
                        'journal_id': int(customer_journal_id),
                        'payment_reference': picking_id.name,
                        'invoice_line_ids': invoice_line_list,
                        'transfer_ids': self,
                        'invoice_payment_term_id':picking_id.purchase_id.payment_term_id.id
                    })
                    for line in invoice.line_ids:
                        if line.account_id.account_type == 'liability_payable':  # Ejemplo: modificar solo cuentas por pagar
                            transfer_details=[]
                            for transfer in invoice.transfer_ids:
                                purchase_name = transfer.origin if transfer.origin else "Sin pedido de compra"
                                transfer_details.append(f"{transfer.name} {purchase_name}")
                            transfer_names = ', '.join(transfer_details)
                            line.name = f"{transfer_names}"
                else:
                    for picking_id in self:
                        picking_id.create_invoice()
            elif all(first.code == 'incoming' for first in picking_type):
                partner = list(self.partner_id)
                if all(first == partner[0] for first in partner):
                    partner_id = self.partner_id
                    bill_line_list = []
                    vendor_journal_id = \
                        self.env['ir.config_parameter'].sudo().\
                            get_param('stock_move_invoice.vendor_journal_id') \
                        or False
                    if not vendor_journal_id:
                        raise UserError(_("Please configure the journal from "
                                            "the settings."))
                    for picking_id in self:
                        for move_ids_without_package in picking_id.\
                                move_ids_without_package:
                            if move_ids_without_package.state=='done':
                                if move_ids_without_package.account_move_line_ids:
                                    total_quantity = sum(line.quantity for line in move_ids_without_package.account_move_line_ids.filtered(lambda x: x.parent_state == 'posted'))
                                    outstanding_quantity = move_ids_without_package.quantity - total_quantity
                                else:
                                    outstanding_quantity=move_ids_without_package.quantity
                                if outstanding_quantity>0:

                                    vals = (0, 0, {
                                        'name':
                                            move_ids_without_package.description_picking
                                        ,
                                        'product_id':
                                            move_ids_without_package.product_id.id,
                                        # 'price_unit': move_ids_without_package.
                                        #     product_id.lst_price,
                                        'price_unit': move_ids_without_package.purchase_line_id.price_unit,
                                        'analytic_distribution': move_ids_without_package.purchase_line_id.analytic_distribution,
                                        'product_uom_id': move_ids_without_package.purchase_line_id.product_uom.id,
                                        'account_id': move_ids_without_package.
                                            product_id.property_account_expense_id.id if
                                        move_ids_without_package.product_id.
                                            property_account_expense_id
                                        else move_ids_without_package.
                                            product_id.categ_id.
                                            property_account_expense_categ_id.id,
                                        # 'tax_ids': [(6, 0, [picking_id.company_id.
                                        #              account_purchase_tax_id.id])],
                                        'discount': move_ids_without_package.purchase_line_id.discount,
                                        'tax_ids': [(6, 0, move_ids_without_package.purchase_line_id.taxes_id.ids or [])],
                                        'quantity':
                                            outstanding_quantity,
                                        'purchase_line_id': move_ids_without_package.purchase_line_id.id,
                                        'stock_move_id': move_ids_without_package.id
                                    })
                                    bill_line_list.append(vals)

                    journal = picking_id.env['account.journal'].search([
                        ('default_compra', '=', True),
                        ('company_id', '=', picking_id.company_id.id)
                    ], limit=1)

                    if not journal:
                        raise UserError(_("No se encontró un Diario con 'Compra' activo para la compañía %s") % picking_id.company_id.display_name)

                    invoice = self.env['account.move'].create({
                        'move_type': 'in_invoice',
                        'invoice_origin': picking_id.name,
                        'invoice_user_id': self.env.uid,
                        'narration': picking_id.name,
                        'partner_id': partner_id.id,
                        'currency_id': picking_id.purchase_id.currency_id.id,
                        'journal_id': journal.id,
                        'payment_reference': picking_id.name,
                        'picking_id': picking_id.id,
                        'invoice_line_ids': bill_line_list,
                        'transfer_ids': self,
                        'invoice_payment_term_id':picking_id.purchase_id.payment_term_id.id
                    })
                    for line in invoice.line_ids:
                        if line.account_id.account_type == 'liability_payable':  # Ejemplo: modificar solo cuentas por pagar
                            transfer_details=[]
                            for transfer in invoice.transfer_ids:
                                purchase_name = transfer.origin if transfer.origin else "Sin pedido de compra"
                                transfer_details.append(f"{transfer.name} {purchase_name}")
                            transfer_names = ', '.join(transfer_details)
                            line.name = f"{transfer_names}"
                else:
                    for picking_id in self:
                        picking_id.create_bill()
        else:
            raise UserError(_("Please select single type transfer"))
