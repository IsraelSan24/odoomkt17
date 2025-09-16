from odoo import api, fields, models
import datetime
from odoo.exceptions import UserError, ValidationError
import json
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_l10n_latam_documents_domain(self):
        self.ensure_one()
        domain = super()._get_l10n_latam_documents_domain()
        if self.journal_id.company_id.country_id != self.env.ref('base.pe') or not \
                self.journal_id.l10n_latam_use_documents:
            return domain
        if self.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code == '1':
            domain += [('code', 'not in', ['01', '09', '00'])]
        domain += [('code', 'not in', ['91', '97', '98'])]
        return domain

    l10n_latam_document_type_code = fields.Char(
        string='Codigo del tipo de documento', related='l10n_latam_document_type_id.code')

    # COMPRAS DETRACCION
    l10n_pe_proof_detraction_deposit_date = fields.Date(
        string='Fecha de emisión de la Constancia de Depósito de Detracción (5)')
    l10n_pe_proof_detraction_deposit_number = fields.Char(
        string='Número de la Constancia de Depósito de Detracción (5)')
    
    l10n_pe_is_subject_to_withholding = fields.Boolean(
        string='Sujeto a Retención')
    l10n_pe_subject_to_withholding_code = fields.Char(
        string='Código de sujeto a retención', compute='_compute_subject_to_withholding_code', store=True)
    
    @api.depends('l10n_pe_is_subject_to_withholding')
    def _compute_subject_to_withholding_code(self):
        for record in self:
            if record.l10n_pe_is_subject_to_withholding:
                record.l10n_pe_subject_to_withholding_code = '1'
            else:
                record.l10n_pe_subject_to_withholding_code = ''
                
    # NO DOMICILIADO
    l10n_pe_is_non_domiciled_bill = fields.Boolean(
        string='No domiciliado', compute='_compute_l10n_pe_is_non_domiciled_bill', store=True)

    @api.depends('partner_id.country_id.code')
    def _compute_l10n_pe_is_non_domiciled_bill(self):
        for record in self:
            if record.partner_id.l10n_pe_is_non_domiciled and record.move_type in ['in_invoice','in_refund','in_receipt']:
                l10n_pe_is_non_domiciled_bill = True
            else:
                l10n_pe_is_non_domiciled_bill = False
            record.l10n_pe_is_non_domiciled_bill = l10n_pe_is_non_domiciled_bill

    l10n_pe_non_domic_sustent_document_type_id = fields.Many2one(
        'l10n_latam.document.type', string='Tipo de documento del Sustento', help='Tipo de Comprobante de Pago o Documento que sustenta el crédito fiscal')
    l10n_pe_non_domic_sustent_serie = fields.Char(
        string='Serie del Sustento', help='Serie del comprobante de pago o documento que sustenta el crédito fiscal. En los casos de la Declaración Única de Aduanas (DUA) o de la Declaración Simplificada de Importación (DSI) se consignará el código de la dependencia Aduanera.')
    l10n_pe_non_domic_sustent_number = fields.Char(
        string='Correlativo del Sustento', help='Número del comprobante de pago o documento o número de orden del formulario físico o virtual donde conste el pago del impuesto, tratándose de la utilización de servicios prestados por no domiciliados u otros, número de la DUA o de la DSI, que sustente el crédito fiscal.')

    l10n_pe_non_domic_sustent_dua_emission_year = fields.Selection([(str(num), str(num)) for num in range(
        1981, (datetime.datetime.now().year+1))], string='Año de emisión DUA o DSI')

    l10n_pe_non_domic_igv_withholding_amount = fields.Float(
        string='Monto de retención del IGV')

    l10n_pe_non_domic_brute_rent_amount = fields.Monetary(string='Renta Bruta')
    l10n_pe_non_domic_disposal_capital_assets_cost = fields.Float(
        string='Costo de Enajenación', help='Deducción / Costo de Enajenación de bienes de capital')
    l10n_pe_non_domic_net_rent_amount = fields.Float(string='Renta Neta')
    l10n_pe_non_domic_withholding_rate = fields.Float(
        string='Tasa de retención')
    l10n_pe_non_domic_withheld_tax = fields.Float(string='Impuesto retenido')

    l10n_pe_edi_table_27_id = fields.Many2one(
        'l10n_pe_edi.table.27', string='Vínculo entre el contribuyente y el residente en el extranjero', help="Tabla 27")

    def _get_default_table_25_id(self):
        table_25_default = self.env['l10n_pe_edi.table.25'].search(
            [('code', '=', '00')], limit=1)
        return table_25_default
    
    def _get_default_table_31_id(self):
        table_31_default = self.env['l10n_pe_edi.table.31'].search(
            [('code', '=', '00')], limit=1)
        return table_31_default
    
    l10n_pe_edi_table_25_id = fields.Many2one(
        'l10n_pe_edi.table.25', string='Convenios para evitar la doble imposición', help="Tabla 25", default=_get_default_table_25_id)
    
    l10n_pe_edi_table_31_id = fields.Many2one(
        'l10n_pe_edi.table.31', string='Tipo de renta', help="Tabla 31", default=_get_default_table_31_id)
    
    l10n_pe_edi_table_32_id = fields.Many2one(
        'l10n_pe_edi.table.32', string='Modalidad del servicio prestado por el no domiciliado', help="Tabla 32")
    
    l10n_pe_edi_table_33_id = fields.Many2one(
        'l10n_pe_edi.table.33', string='Exoneración aplicada', help="Tabla 33")  

    l10n_pe_non_domic_is_tax_rent_applied = fields.Boolean(
        string='Aplicación de Impuesto a la renta', help='Aplicación del penúltimo parrafo del Art. 76° de la Ley del Impuesto a la Renta')
    l10n_pe_non_domic_tax_rent_code = fields.Char(
        string='Código de aplicación de impuesto a la renta', compute='_compute_l10n_pe_non_domic_tax_rent_code', store=True)

    l10n_pe_ple_8_2_status = fields.Selection(string='Estado PLE no domic', selection=[
        ('0', 'La operación (anotación optativa sin efecto en el IGV) corresponde al periodo. '),
        ('9', 'Ajuste o rectificación en la anotación de la información de una operación registrada en un periodo anterior.')],
        default='0',
        help='Estado que identifica la oportunidad de la anotación o indicación si ésta corresponde a un ajuste.')

    @api.depends('l10n_pe_non_domic_is_tax_rent_applied')
    def _compute_l10n_pe_non_domic_tax_rent_code(self):
        for record in self:
            if record.l10n_pe_non_domic_is_tax_rent_applied:
                record.l10n_pe_non_domic_tax_rent_code = '1'
            else:
                record.l10n_pe_non_domic_tax_rent_code = ''

    # Datos del proveedor
    l10n_pe_partner_name = fields.Char(
        'Razón social del proveedor', related='partner_id.name')
    l10n_pe_partner_street = fields.Char(
        'Dirección del proveedor', related='partner_id.street')
    l10n_pe_partner_vat = fields.Char(
        'Número de identificación del proveedor', related='partner_id.vat')
                
    # DUAs
    l10n_pe_edi_table_11_id = fields.Many2one(
        'l10n_pe_edi.table.11', string='Dependencia aduanera', help='Dependencia aduanera (Tabla 11)')
    l10n_pe_edi_table_11_code = fields.Char(
        string='Serie Aduana', related='l10n_pe_edi_table_11_id.code')
    l10n_pe_dua_emission_year = fields.Selection([(str(num), str(num)) for num in range(
        1981, (datetime.datetime.now().year+1))], string='Año de emisión DUA o DSI')

    
    def _get_default_table_30_id(self):
        table_30_default = self.env['l10n_pe_edi.table.30'].search(
            [('code', '=', '1')], limit=1)
        return table_30_default
    
    l10n_pe_edi_table_30_id = fields.Many2one('l10n_pe_edi.table.30', string='Clasificación de los bienes y servicios adquiridos',
                                              default=_get_default_table_30_id,
                                              help='Tabla 30')

    @api.onchange('l10n_pe_edi_table_11_id')
    def _onchange_l10n_pe_edi_table_11_id(self):
        self.l10n_pe_in_edi_serie = self.l10n_pe_edi_table_11_code

    l10n_pe_in_edi_serie = fields.Char(string='Serie', copy=False)
    l10n_pe_in_edi_number = fields.Char(string='N°', copy=False)

    @api.onchange('l10n_pe_in_edi_number')
    def _onchange_l10n_pe_in_edi_number(self):
        l10n_pe_in_edi_number = self.l10n_pe_in_edi_number
        if l10n_pe_in_edi_number:
            self.l10n_pe_in_edi_number = l10n_pe_in_edi_number.zfill(8)
        else:
            self.l10n_pe_in_edi_number = l10n_pe_in_edi_number

    @api.onchange('l10n_pe_in_edi_serie')
    def _onchange_l10n_pe_in_edi_serie(self):
        l10n_pe_in_edi_serie = self.l10n_pe_in_edi_serie
        if l10n_pe_in_edi_serie:
            if len(l10n_pe_in_edi_serie) > 4:
                raise ValidationError(
                    'La serie debe tener como máximo 4 dígitos.')
        else:
            self.l10n_pe_in_edi_serie = l10n_pe_in_edi_serie

    @api.depends('name', 'l10n_pe_in_edi_serie', 'l10n_pe_in_edi_number')
    def _compute_l10n_latam_document_number(self):
        recs_with_name = self.filtered(lambda x: x.name != '/')
        _logger.info("recs_with_name")
        _logger.info(recs_with_name)
        for rec in recs_with_name:
            name = rec.name
            _logger.info("name")
            _logger.info(name)
            if rec.l10n_pe_in_edi_serie and rec.l10n_pe_in_edi_number:
                new_name = f"{rec.l10n_pe_in_edi_serie}-{rec.l10n_pe_in_edi_number}"
            else:
                new_name = False
            doc_code_prefix = rec.l10n_latam_document_type_id.doc_code_prefix
            _logger.info("doc_code_prefix")
            _logger.info(doc_code_prefix)
            if doc_code_prefix and name:
                name = name.split(" ", 1)[-1]
                _logger.info("name split")
                _logger.info(name)
            if new_name and name != new_name:
                _logger.info("new_name")
                _logger.info(new_name)
                name = new_name
            rec.l10n_latam_document_number = name
        remaining = self - recs_with_name
        _logger.info("remaining")
        _logger.info(remaining)
        for rem in remaining:
            if rem.l10n_pe_in_edi_serie and rem.l10n_pe_in_edi_number:
                rem.l10n_latam_document_number = f"{rem.l10n_pe_in_edi_serie}-{rem.l10n_pe_in_edi_number}"
            else:
                rem.l10n_latam_document_number = False

    l10n_pe_in_edi_serie = fields.Char(
        string='Serie',
        copy=False,
        default='F001'
    )

    l10n_pe_in_edi_number = fields.Char(
        string='N°',
        copy=False,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('l10n_pe_edi.invoice.number') or '*'
    )

    def _get_invoice_serie_number(self):
        for move in self:
            if move.name:
                inv_number = move.name.split('-')
            else:
                inv_number = []
            if move.name and move.move_type != 'entry' and len(inv_number) == 2:
                inv_serie = inv_number[0].split(' ')
                if len(inv_serie) == 2:
                    serie = inv_serie[1]
                else:
                    serie = inv_number[0]
                move.l10n_pe_invoice_serie = serie
                move.l10n_pe_invoice_number = inv_number[1]
            else:
                move.l10n_pe_invoice_serie = False
                move.l10n_pe_invoice_number = False

    l10n_pe_edi_reversal_serie = fields.Char(
        string='Document serie', help='Used for Credit and debit note', readonly=False)
    l10n_pe_edi_reversal_number = fields.Char(
        string='Document number', help='Used for Credit and debit note', readonly=False)
    l10n_pe_edi_reversal_date = fields.Date(
        string='Document date', help='Date of the Credit or debit note', readonly=False)

    # === Amount fields ===
    l10n_pe_edi_amount_subtotal = fields.Monetary(
        string='Subtotal', readonly=True, compute='_compute_lines_amounts', help="Total sin impuestos y descuentos")
    l10n_pe_edi_amount_discount = fields.Monetary(
        string='Decuento',  readonly=True, compute='_compute_lines_amounts')
    l10n_pe_edi_amount_base = fields.Monetary(
        string='Base imponible',  readonly=True, compute='_compute_lines_amounts', help="Total con descuentos antes de impuestos")
    l10n_pe_edi_amount_exonerated = fields.Monetary(
        string='Monto Exonerado',  compute='_compute_lines_amounts')
    l10n_pe_edi_amount_free = fields.Monetary(
        string='Gratis',  compute='_compute_lines_amounts')
    l10n_pe_edi_amount_unaffected = fields.Monetary(
        string='Inafecto',  compute='_compute_lines_amounts')
    l10n_pe_edi_amount_untaxed = fields.Monetary(
        string='Total antes de impuestos',  compute='_compute_lines_amounts', help="Total antes de impuestos con descuento incluido")
    l10n_pe_edi_global_discount = fields.Monetary(
        string='Descuento Global',  readonly=True, compute='_compute_lines_amounts')
    l10n_pe_edi_amount_in_words = fields.Char(
        string="Monto en palabras", compute='_l10n_pe_edi_amount_in_words')

    l10n_pe_edi_amount_unaffected_discount = fields.Monetary(
        string='Descuento a inafecto',  compute='_compute_lines_amounts')
    l10n_pe_edi_amount_unaffected_with_discount = fields.Monetary(
        string='Inafecto con descuento',  compute='_compute_lines_amounts')

    l10n_pe_edi_amount_exonerated_discount = fields.Monetary(
        string='Descuento a exonerado',  compute='_compute_lines_amounts')
    l10n_pe_edi_amount_exonerated_with_discount = fields.Monetary(
        string='Exonerado con descuento',  compute='_compute_lines_amounts')

    # ==== Tax fields ====
    l10n_pe_edi_amount_icbper = fields.Monetary(
        string='ICBPER Amount', compute='_compute_lines_amounts')
    l10n_pe_edi_amount_igv = fields.Monetary(
        string='Monto IGV', compute='_compute_lines_amounts')

    l10n_pe_edi_amount_isc = fields.Monetary(
        string='Monto ISC',  compute='_compute_lines_amounts')

    l10n_pe_edi_amount_ivap = fields.Monetary(
        string='Monto IVAP', compute='_compute_lines_amounts')
    l10n_pe_edi_amount_others = fields.Monetary(
        string='Otros tributos', compute='_compute_lines_amounts')

    l10n_pe_edi_amount_discount_base = fields.Monetary(
        string='Descuento de la base imponible',  readonly=True, compute='_compute_lines_amounts')
    l10n_pe_edi_amount_discount_igv = fields.Monetary(
        string='Descuento del IGV',  readonly=True, compute='_compute_lines_amounts')

    def _l10n_pe_prepare_tax_dict(self):
        document = {
            'amount_total': self.amount_total,
            'tax_details': {
                'total_excluded': 0.0,
                'total_included': 0.0,
                'total_taxes': 0.0,
            },
            "discount_global_base": 0,
            "discount_global_amount": 0,
        }
        tax_details = document['tax_details']

        tax_res_grouped = {}
        invoice_line_vals = []
        discount_global_base = 0
        for line in self.invoice_line_ids:
            dic_line = line._l10n_pe_prepare_tax_dict_lines()
            for tax_res in dic_line['tax_details']['taxes']:
                tuple_key = (
                    tax_res['l10n_pe_edi_group_code'],
                    tax_res['l10n_pe_edi_international_code'],
                    tax_res['l10n_pe_edi_tax_code'],
                )
                tax_res_grouped.setdefault(tuple_key, {
                    'base': 0.0,
                    'amount': 0.0,
                    'l10n_pe_edi_group_code': tax_res['l10n_pe_edi_group_code'],
                    'l10n_pe_edi_international_code': tax_res['l10n_pe_edi_international_code'],
                    'l10n_pe_edi_tax_code': tax_res['l10n_pe_edi_tax_code'],
                })
                tax_res_grouped[tuple_key]['base'] += tax_res['base']
                tax_res_grouped[tuple_key]['amount'] += tax_res['amount']

                tax_details['total_excluded'] += tax_res['base']
                tax_details['total_included'] += tax_res['base'] + \
                    tax_res['amount']
                tax_details['total_taxes'] += tax_res['amount']

                if dic_line.get('price_total') < 0:
                    document['discount_global_amount'] += abs(tax_res['base'])
                else:
                    discount_global_base += tax_res['base']
                    invoice_line_vals.append(dic_line)

        if document['discount_global_amount'] > 0:
            document["discount_global_type"] = "02"
            document["discount_global_base"] = discount_global_base
        document['items'] = invoice_line_vals
        document['tax_details']['grouped_taxes'] = list(
            tax_res_grouped.values())
        return document

    def _compute_lines_amounts(self):
        for move in self:
            if move.move_type not in ['entry']:
                base_dte = move._l10n_pe_prepare_tax_dict()
                conflux_dte = {
                    "total_gravado": 0,
                    "total_exonerado": 0,
                    "total_inafecto": 0,
                    "total_gratuito": 0,
                    "total_base_isc": 0,
                    "total_igv": 0,
                    "total_isc": 0,
                    "total": base_dte.get('amount_total'),
                    "descuento_base": base_dte.get('discount_global_base'),
                    "descuento_importe": base_dte.get('discount_global_amount'),
                }
                for subtotal in base_dte['tax_details']['grouped_taxes']:
                    if subtotal['l10n_pe_edi_tax_code'] == '1000':
                        conflux_dte['total_gravado'] += subtotal['base']
                        conflux_dte['total_igv'] += subtotal['amount']
                    if subtotal['l10n_pe_edi_tax_code'] == '2000':
                        conflux_dte['total_base_isc'] += subtotal['base']
                        conflux_dte['total_isc'] += subtotal['amount']
                    elif subtotal['l10n_pe_edi_tax_code'] == '9996':
                        conflux_dte['total_gratuito'] += subtotal['base']
                    elif subtotal['l10n_pe_edi_tax_code'] == '9997':
                        conflux_dte['total_exonerado'] += subtotal['base']
                    elif subtotal['l10n_pe_edi_tax_code'] == '9998':
                        conflux_dte['total_inafecto'] += subtotal['base']
                conflux_dte['descuento_importe'] = abs(
                    conflux_dte['descuento_importe'])
                if conflux_dte['total_exonerado'] == conflux_dte['descuento_importe']:
                    conflux_dte['total_exonerado'] = 0
                if round(conflux_dte['total_gravado'] + conflux_dte['total_exonerado'] + conflux_dte['total_inafecto'] + conflux_dte['total_igv'], 2) == conflux_dte['total']:
                    conflux_dte['descuento_importe'] = 0
                move.write({
                    'l10n_pe_edi_amount_base': conflux_dte['total_gravado'],
                    'l10n_pe_edi_amount_igv': move.find_igv_amount(),
                    'l10n_pe_edi_amount_isc': move.find_isc_amount(),
                    'l10n_pe_edi_amount_ivap': False,
                    'l10n_pe_edi_amount_icbper': move.find_icbper_amount(),
                    'l10n_pe_edi_amount_exonerated': conflux_dte['total_exonerado'],
                    'l10n_pe_edi_amount_unaffected': conflux_dte['total_inafecto'],
                    'l10n_pe_edi_amount_free': conflux_dte['total_gratuito'],
                    'l10n_pe_edi_amount_discount': False,
                    'l10n_pe_edi_global_discount': False,
                    'l10n_pe_edi_amount_subtotal': False,
                    'l10n_pe_edi_amount_untaxed': False,
                    'l10n_pe_edi_amount_unaffected_discount': False,
                    'l10n_pe_edi_amount_unaffected_with_discount': False,
                    'l10n_pe_edi_amount_exonerated_discount': False,
                    'l10n_pe_edi_amount_exonerated_with_discount': conflux_dte['total_exonerado'] - conflux_dte['descuento_importe'],
                    'l10n_pe_edi_amount_others': move.find_percepcion_amount(),
                    'l10n_pe_edi_amount_discount_base': False,
                    'l10n_pe_edi_amount_discount_igv': False,
                })
            else:
                move.write({
                    'l10n_pe_edi_amount_base': False,
                    'l10n_pe_edi_amount_igv': False,
                    'l10n_pe_edi_amount_isc': False,
                    'l10n_pe_edi_amount_ivap': False,
                    'l10n_pe_edi_amount_icbper': False,
                    'l10n_pe_edi_amount_exonerated': False,
                    'l10n_pe_edi_amount_unaffected': False,
                    'l10n_pe_edi_amount_free': False,
                    'l10n_pe_edi_amount_discount': False,
                    'l10n_pe_edi_global_discount': False,
                    'l10n_pe_edi_amount_subtotal': False,
                    'l10n_pe_edi_amount_untaxed': False,
                    'l10n_pe_edi_amount_unaffected_discount': False,
                    'l10n_pe_edi_amount_unaffected_with_discount': False,
                    'l10n_pe_edi_amount_exonerated_discount': False,
                    'l10n_pe_edi_amount_exonerated_with_discount': False,
                    'l10n_pe_edi_amount_others': False,
                    'l10n_pe_edi_amount_discount_base': False,
                    'l10n_pe_edi_amount_discount_igv': False,
                })

    def _l10n_pe_vat_validation(self):
        for record in self:
            partner_pe_vat_code = record.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code
            partner_vat = record.partner_id.vat
            document_code = record.l10n_latam_document_type_id.code
            if document_code == '01' and partner_pe_vat_code != '6' or partner_vat == False:
                raise UserError(
                    'Para emitir facturas se debe asignar el RUC al cliente.')
                
    def action_post(self):
        self._l10n_pe_vat_validation()
        super(AccountMove, self).action_post()

    def _get_starting_sequence(self):
        if self.journal_id.l10n_latam_use_documents and self.env.company.country_id.code == "PE":
            if self.l10n_latam_document_type_id:
                if self.l10n_latam_document_type_id.code:
                    return '%s %s-00000000' % (self.l10n_latam_document_type_id.doc_code_prefix or "", self.journal_id.code)
                else:
                    return '%s-00000000' % (self.journal_id.code)
        return super()._get_starting_sequence()

    def _get_tax_amount_by_group(self, group_name):
        self.ensure_one()
        lines = self.line_ids.filtered(
            lambda l: l.tax_line_id and l.tax_line_id.tax_group_id.name == group_name
        )
        return sum(lines.mapped('credit')) - sum(lines.mapped('debit'))

    def find_igv_amount(self):
        return self._get_tax_amount_by_group('IGV')

    def find_unaffected_amount(self):
        return self._get_tax_amount_by_group('INA')

    def find_isc_amount(self):
        return self._get_tax_amount_by_group('ISC')

    def find_percepcion_amount(self):
        return self._get_tax_amount_by_group('PERC')

    def find_icbper_amount(self):
        return self._get_tax_amount_by_group('ICBPER')

    def base_amount(self):
        """Retorna el monto base (subtotal sin impuestos)."""
        self.ensure_one()
        return sum(self.invoice_line_ids.mapped('price_subtotal'))