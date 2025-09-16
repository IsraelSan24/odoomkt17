import logging

from odoo import api, fields, models, _
_logger = logging.getLogger(__name__)

def unit_amount(amount, quantity, currency):
    ''' Helper to divide amount by quantity by taking care about float division by zero. '''
    if quantity:
        return currency.round(amount / quantity)
    else:
        return 0.0
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    def _get_igv_type(self):
        return self.env['l10n_pe_edi.catalog.07'].search([('code','=','10')], limit=1)
    
    # ==== Business fields ====
    l10n_pe_edi_price_base = fields.Monetary(string='Subtotal without discounts', store=True, readonly=True, currency_field='currency_id', help="Total amount without discounts and taxes")
    l10n_pe_edi_price_unit_excluded = fields.Monetary(string='Price unit excluded', store=True, readonly=True, currency_field='currency_id', help="Price unit without taxes")
    l10n_pe_edi_price_unit_included = fields.Monetary(string='Price unit IGV included', store=True, readonly=True, currency_field='currency_id', help="Price unit with IGV included")
    l10n_pe_edi_amount_discount = fields.Monetary(string='Amount discount before taxes', store=True, readonly=True, currency_field='currency_id', help='Amount discount before taxes')
    l10n_pe_edi_amount_free = fields.Monetary(string='Amount free', store=True, readonly=True, currency_field='currency_id', help='amount calculated if the line id for free product')
    l10n_pe_edi_free_product = fields.Boolean('Free', store=True, readonly=True, default=False, help='Is free product?')
    # ==== Tax fields ====    
    l10n_pe_edi_igv_type = fields.Many2one('l10n_pe_edi.catalog.07', string="Type of IGV", compute='_compute_igv_type', store=True, readonly=False)
    #l10n_pe_edi_isc_type = fields.Many2one('l10n_pe_edi.catalog.08', string="Type of ISC", compute='_compute_isc_type', store=True, readonly=False)
    l10n_pe_edi_igv_amount = fields.Monetary(string='IGV amount',store=True, readonly=True, currency_field='currency_id', help="Total IGV amount")
    
    l10n_pe_edi_isc_amount = fields.Monetary(string='ISC amount',store=True, readonly=True, currency_field='currency_id', help="Total ISC amount")
    l10n_pe_edi_icbper_amount = fields.Monetary(string='ICBPER amount',store=True, readonly=True, currency_field='currency_id', help="Total ICBPER amount")
    
    @api.depends('tax_ids','l10n_pe_edi_free_product')
    def _compute_igv_type(self):
        for line in self:
            if line.discount >= 100.0:  
                # Discount >= 100% means the product is free and the IGV type should be 'No onerosa' and 'taxed'
                l10n_pe_edi_igv_type = self.env['l10n_pe_edi.catalog.07'].search([('type','=','taxed'),('no_onerosa','=',True)], limit=1).id
            elif any(tax.l10n_pe_edi_tax_code in ['1000'] for tax in line.tax_ids):
                # Tax with code '1000' is IGV
                l10n_pe_edi_igv_type = self.env['l10n_pe_edi.catalog.07'].search([('code','=','10')], limit=1).id
            elif all(tax.l10n_pe_edi_tax_code in ['9997'] for tax in line.tax_ids):
                # Tax with code '9997' is Exonerated
                l10n_pe_edi_igv_type = self.env['l10n_pe_edi.catalog.07'].search([('type','=','exonerated')], limit=1).id
            elif all(tax.l10n_pe_edi_tax_code in ['9998'] for tax in line.tax_ids):
                # Tax with code '9998' is Unaffected
                l10n_pe_edi_igv_type = self.env['l10n_pe_edi.catalog.07'].search([('type','=','unaffected')], limit=1).id
            elif all(tax.l10n_pe_edi_tax_code in ['9995'] for tax in line.tax_ids):
                # Tax with code '9995' is for Exportation
                l10n_pe_edi_igv_type = self.env['l10n_pe_edi.catalog.07'].search([('type','=','exportation')], limit=1).id
            else:
                l10n_pe_edi_igv_type = self.env['l10n_pe_edi.catalog.07'].search([('code','=','10')], limit=1).id
            _logger.info("l10n_pe_edi_igv_type")
            _logger.info(l10n_pe_edi_igv_type)
            line.l10n_pe_edi_igv_type = l10n_pe_edi_igv_type
    
    
    def _l10n_pe_prepare_tax_dict_lines(self):
        price_unit_wo_discount = self.price_unit * \
            (1.0 - (self.discount or 0.0) / 100.0)
        taxes_res = self.tax_ids.compute_all(
            price_unit_wo_discount,
            currency=self.move_id.currency_id,
            quantity=self.quantity,
            product=self.product_id,
            partner=self.partner_id,
            is_refund=self.move_id.move_type in ('out_refund', 'in_refund'),
        )
        taxes_res.update({
            'unit_total_included': unit_amount(taxes_res['total_included'], self.quantity, self.move_id.currency_id),
            'unit_total_excluded': unit_amount(taxes_res['total_excluded'], self.quantity, self.move_id.currency_id),
            'price_unit_type_code': '01' if not self.move_id.currency_id.is_zero(price_unit_wo_discount) else '02',
        })

        for tax_res in taxes_res['taxes']:
            tax = self.env['account.tax'].browse(tax_res['id'])
            # TODO 
            if self.price_subtotal == 0 and tax.l10n_pe_edi_tax_code != '7152':
                tax_l10n_pe_edi_tax_code = '9996'
                tax_l10n_pe_edi_igv_type = '11'
                tax_l10n_pe_edi_isc_type = False
                tax_tax_group_id_l10n_pe_edi_code = 'GRA'
                tax_l10n_pe_edi_international_code = 'FRE'
            else:
                tax_l10n_pe_edi_tax_code = tax.l10n_pe_edi_tax_code
                tax_l10n_pe_edi_igv_type = tax.l10n_pe_edi_igv_type
                tax_l10n_pe_edi_isc_type = tax.l10n_pe_edi_isc_type
                tax_tax_group_id_l10n_pe_edi_code = tax.tax_group_id.l10n_pe_edi_code
                tax_l10n_pe_edi_international_code = tax.l10n_pe_edi_international_code
            tax_res.update({
                'tax_amount': tax.amount,
                'tax_amount_type': tax.amount_type,
                'price_unit_type_code': '01' if not self.move_id.currency_id.is_zero(tax_res['amount']) else '02',
                'l10n_pe_edi_tax_code': tax_l10n_pe_edi_tax_code,
                'l10n_pe_edi_group_code': tax_tax_group_id_l10n_pe_edi_code,
                'l10n_pe_edi_international_code': tax_l10n_pe_edi_international_code,
                'l10n_pe_edi_affectation_reason': tax_l10n_pe_edi_igv_type,
                'l10n_pe_edi_isc_type_computation': tax_l10n_pe_edi_isc_type,
            })

        line = {
            'name': self.name,
            'quantity': self.quantity,
            'price_subtotal': self.price_subtotal,
            'price_total': self.price_total,
            'tax_details': taxes_res,
            'discount_base': 0,
            'discount_amount': 0,
        }
        if self.discount > 0:
            line['discount_type'] = '00'
            line['discount_factor'] = (self.discount or 0.0) / 100.0
            if line['discount_factor'] != 1:
                discount_base= self.price_subtotal / \
                (1.0 - line['discount_factor'])
            else:
                discount_base = self.price_unit
            line['discount_base'] = discount_base
            line['discount_amount'] = line['discount_base'] * \
                line['discount_factor']

        return line
    
    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type):
        ''' This method is used to compute 'price_total' & 'price_subtotal'. '''
        
        # Lógica personalizada para calcular los valores
        res = {}  # Diccionario de resultados
        
        # Cálculos básicos
        l10n_pe_edi_price_base = quantity * price_unit
        l10n_pe_edi_price_unit_included = price_unit
        l10n_pe_edi_igv_amount = 0.0
        l10n_pe_edi_isc_amount = 0.0
        l10n_pe_edi_icbper_amount = 0.0
        
        if taxes:
            # Calcula impuestos para toda la línea
            taxes_res = taxes._origin.compute_all(price_unit, quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
            
            l10n_pe_edi_price_unit_excluded = l10n_pe_edi_price_unit_excluded_signed = quantity != 0 and taxes_res['total_excluded']/quantity or 0.0
            res['l10n_pe_edi_price_unit_excluded'] = l10n_pe_edi_price_unit_excluded
            l10n_pe_edi_price_unit_included = l10n_pe_edi_price_unit_included_signed = quantity != 0 and taxes_res['total_included']/quantity or 0.0
            res['l10n_pe_edi_price_unit_included'] = l10n_pe_edi_price_unit_included
            
            # Calcula los impuestos con descuento
            taxes_discount = taxes.compute_all(price_unit * (1 - (discount or 0.0) / 100.0), currency, quantity, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
            
            # Impuestos IGV
            igv_taxes_ids = taxes.filtered(lambda r: r.tax_group_id.name == 'IGV')
            if igv_taxes_ids:
                l10n_pe_edi_price_unit_included = l10n_pe_edi_price_unit_included_signed = quantity != 0 and taxes_res['total_included']/quantity or 0.0 if igv_taxes_ids else price_unit
                res['l10n_pe_edi_price_unit_included'] = l10n_pe_edi_price_unit_included
                l10n_pe_edi_igv_amount = sum(r['amount'] for r in taxes_discount['taxes'] if r['id'] in igv_taxes_ids.ids)
            
            l10n_pe_edi_price_base = l10n_pe_edi_price_base_signed = taxes_res['total_excluded']
            res['l10n_pe_edi_price_base'] = l10n_pe_edi_price_base
            
            # Impuestos ISC
            isc_taxes_ids = taxes.filtered(lambda r: r.tax_group_id.name == 'ISC')
            if isc_taxes_ids:
                l10n_pe_edi_isc_amount = sum(r['amount'] for r in taxes_discount['taxes'] if r['id'] in isc_taxes_ids.ids)
            
            # Impuestos ICBPER
            icbper_taxes_ids = taxes.filtered(lambda r: r.tax_group_id.name == 'ICBPER')
            if icbper_taxes_ids:
                l10n_pe_edi_icbper_amount = sum(r['amount'] for r in taxes_discount['taxes'] if r['id'] in icbper_taxes_ids.ids)

        # Monto de descuento si es gratis
        if discount >= 100.0:
            l10n_pe_edi_igv_amount = 0.0
            l10n_pe_edi_isc_amount = 0.0
            l10n_pe_edi_icbper_amount = 0.0
            l10n_pe_edi_amount_discount = 0.0
            l10n_pe_edi_free_product = True
            l10n_pe_edi_amount_free = price_unit * quantity
        else:
            l10n_pe_edi_amount_discount = (l10n_pe_edi_price_unit_included * discount * quantity) / 100
            l10n_pe_edi_free_product = False
            l10n_pe_edi_amount_free = 0.0

        # Asignación a res para los valores calculados
        res['l10n_pe_edi_amount_discount'] = l10n_pe_edi_amount_discount
        res['l10n_pe_edi_amount_free'] = l10n_pe_edi_amount_free
        res['l10n_pe_edi_free_product'] = l10n_pe_edi_free_product
        res['l10n_pe_edi_igv_amount'] = l10n_pe_edi_igv_amount
        res['l10n_pe_edi_isc_amount'] = l10n_pe_edi_isc_amount
        res['l10n_pe_edi_icbper_amount'] = l10n_pe_edi_icbper_amount
        
        return res
