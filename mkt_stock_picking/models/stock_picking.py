from odoo import fields, models, api
from odoo.tools import UserError
from odoo.exceptions import ValidationError
import logging
import requests
import json

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    gre_doc_name = fields.Char(string='Nombre del Documento', compute='_compute_doc_name', required=False, store=True)
    is_outgoing = fields.Boolean(string="¿Es salida?")

    ############ GENERAL ############

    gre_operacion = fields.Char(string='Operación', size=12, default='generar_guia')
    gre_tipo_de_comprobante = fields.Selection(
        [('7', 'GUÍA REMISIÓN REMITENTE'), 
         ('8', 'GUÍA REMISIÓN TRANSPORTISTA')], 
         string='Tipo de Comprobante', default='8')
    gre_serie = fields.Char(string='Serie', size=4, default='VVV1')
    gre_numero = fields.Integer(string='Número')
    
    gre_cliente_tipo_de_documento = fields.Selection(
        [('6', 'RUC'), 
         ('1', 'DNI'), 
         ('4', 'CARNET DE EXTRANJERÍA'), 
         ('7', 'PASAPORTE'), 
         ('A', 'CÉDULA DIPLOMÁTICA'), 
         ('0', 'NO DOMICILIADO')], 
         string='Tipo de Documento del Remitente', default='6')

    gre_cliente_numero_de_documento = fields.Char(string='Número de Documento del Remitente', related='partner_id.vat', store=True, required=False, size=15) # Para transportistas: Remitente | Para remitentes: Destinatario
    gre_cliente_denominacion = fields.Char(string='Denominación del Remitente', related='partner_id.name', store=True, required=False, size=100)
    gre_cliente_direccion = fields.Char(string='Dirección del Remitente', related='partner_id.street', store=True, required=False, size=100)

    gre_fecha_de_emision = fields.Date(string='Fecha de Emisión', default=lambda self: self.scheduled_date)
    gre_fecha_de_inicio_de_traslado = fields.Date(string='Fecha de Inicio de Traslado', default=lambda self: self.scheduled_date)
    gre_enviar_automaticamente_al_cliente = fields.Boolean(string='Enviar Automáticamente al Cliente', default=False)
    
    gre_peso_bruto_total = fields.Float(string='Peso Bruto Total', digits=(12, 10))
    gre_peso_bruto_unidad_de_medida = fields.Selection(
        [('KGM', 'Kilogramos'), 
         ('TNE', 'Toneladas')], 
         string='Unidad de Medida Peso')
    
    gre_punto_de_partida_ubigeo = fields.Char(string='Ubigeo Punto de Partida', size=6, compute="_compute_ubigeo_partida", store=True, readonly=False)
    gre_punto_de_partida_ubigeo
    gre_punto_de_partida_direccion = fields.Char(string='Dirección Punto de Partida', related='partner_id.street', store=True, size=150)


    gre_punto_de_llegada_ubigeo = fields.Char(string='Ubigeo Punto de Llegada', size=6, compute="_compute_ubigeo_llegada", store=True, readonly=False)
    gre_punto_de_llegada_direccion = fields.Char(string='Dirección Punto de Llegada', size=150)

    gre_transportista_placa_numero = fields.Char(string='Placa Número Transportista', size=8)


    ########## SOLO TRANSPORTISTA ##########
    gre_conductor_documento_tipo = fields.Selection(
        [('1', 'DNI'), 
         ('4', 'CARNET DE EXTRANJERÍA'), 
         ('7', 'PASAPORTE'), 
         ('A', 'CÉDULA DIPLOMÁTICA'), 
         ('0', 'NO DOMICILIADO')], 
         string='Tipo Documento Conductor', default='1')
    
    gre_driver_employee_id = fields.Many2one('hr.employee', string="Empleado transportista", domain=[('job_id.name', 'in', ['TRANSPORTISTA', 'CONDUCTOR'] )])
    gre_conductor_documento_numero = fields.Char(string='Número Documento Conductor', size=15)
    gre_conductor_denominacion = fields.Char(string='Denominación Conductor', size=100)
    gre_conductor_nombre = fields.Char(string='Nombre Conductor', size=250)
    gre_conductor_apellidos = fields.Char(string='Apellidos Conductor', size=250)
    gre_conductor_numero_licencia = fields.Char(string='Número Licencia Conductor', size=10)

    gre_destinatario_documento_tipo = fields.Selection(
        [('6', 'RUC'), 
         ('1', 'DNI'), 
         ('4', 'CARNET DE EXTRANJERÍA'), 
         ('7', 'PASAPORTE'), 
         ('A', 'CÉDULA DIPLOMÁTICA'), 
         ('0', 'NO DOMICILIADO')], 
         string='Tipo Documento Destinatario', default='6')
    gre_destinatario_documento_numero = fields.Char(string='Número Documento Destinatario', size=15)
    gre_destinatario_denominacion = fields.Char(string='Denominación Destinatario', size=100)


    ############ SOLO REMITENTE ############ 
    # motivo_de_traslado = fields.Selection(
    #     [('01', 'VENTA'), 
    #      ('14', 'VENTA SUJETA A CONFIRMACION DEL COMPRADOR'), 
    #      ('02', 'COMPRA'), 
    #      ('04', 'TRASLADO ENTRE ESTABLECIMIENTOS DE LA MISMA EMPRESA'), 
    #      ('18', 'TRASLADO EMISOR ITINERANTE CP'), 
    #      ('08', 'IMPORTACION'), 
    #      ('09', 'EXPORTACION'), 
    #      ('13', 'OTROS'), 
    #      ('05', 'CONSIGNACION'), 
    #      ('17', 'TRASLADO DE BIENES PARA TRANSFORMACION'), 
    #      ('03', 'VENTA CON ENTREGA A TERCEROS'), 
    #      ('06', 'DEVOLUCION'), 
    #      ('07', 'RECOJO DE BIENES TRANSFORMADOS')], 
    #      string='Motivo de Traslado')
    # documento_relacionado_codigo = fields.Char(string='Código Documento Relacionado', size=23)
    # numero_de_bultos = fields.Float(string='Número de Bultos', digits=(6, 0))
    # tipo_de_transporte = fields.Selection(
    #     [('01', 'TRANSPORTE PÚBLICO'), 
    #      ('02', 'TRANSPORTE PRIVADO')], 
    #      string='Tipo de Transporte')
    # transportista_documento_tipo = fields.Selection([('6', 'RUC')], string='Tipo Documento Transportista')
    # transportista_documento_numero = fields.Char(string='Número Documento Transportista', size=11)
    # transportista_denominacion = fields.Char(string='Denominación Transportista', size=100)
    # punto_de_partida_codigo_establecimiento_sunat = fields.Char(string='Código Establecimiento SUNAT Partida', size=4)
    # punto_de_llegada_codigo_establecimiento_sunat = fields.Char(string='Código Establecimiento SUNAT Llegada', size=4)

    ## OPTIONAL
    # cliente_email = fields.Char(string='Email del Cliente', related='company_id.partner_id.email', size=250)
    # cliente_email_1 = fields.Char(string='Email 1 del Cliente', size=250)
    # cliente_email_2 = fields.Char(string='Email 2 del Cliente', size=250)
    # observaciones = fields.Html(string='Observaciones')
    # formato_de_pdf = fields.Char(string='Formato de PDF', size=5)

    # motivo_de_traslado_otros_descripcion = fields.Char(string='Descripción Otros Motivo', size=70)
    # tuc_vehiculo_principal = fields.Char(string='TUC Vehículo Principal', size=15)
    # mtc = fields.Char(string='MTC', size=20)

    # sunat_envio_indicador = fields.Selection(
    #     [('01', 'SUNAT_Envio_IndicadorPagadorFlete_Remitente'), 
    #      ('02', 'SUNAT_Envio_IndicadorPagadorFlete_Subcontratador'), 
    #      ('03', 'SUNAT_Envio_IndicadorPagadorFlete_Tercero'), 
    #      ('04', 'SUNAT_Envio_IndicadorRetornoVehiculoEnvaseVacio'), 
    #      ('05', 'SUNAT_Envio_IndicadorRetornoVehiculoVacio'), 
    #      ('06', 'SUNAT_Envio_IndicadorTrasladoVehiculoM1L')], 
    #      string='Indicador Envío SUNAT')
    # # SI sunat_envio_indicador
    # subcontratador_documento_tipo = fields.Selection([('6', 'RUC')], string='Tipo Documento Subcontratador')
    # subcontratador_documento_numero = fields.Char(string='Número Documento Subcontratador', size=11)
    # subcontratador_denominacion = fields.Char(string='Denominación Subcontratador', size=250)
    # pagador_servicio_documento_tipo_identidad = fields.Selection(
    #     [('6', 'RUC'), 
    #      ('1', 'DNI'), 
    #      ('4', 'CARNET DE EXTRANJERÍA'), 
    #      ('7', 'PASAPORTE'),
    #      ('A', 'CÉDULA DIPLOMÁTICA'),
    #      ('0', 'NO DOMICILIADO')], 
    #      string='Tipo Documento Pagador Servicio')
    # pagador_servicio_documento_numero_identidad = fields.Char(string='Número Documento Pagador Servicio', size=15)
    # pagador_servicio_denominacion = fields.Char(string='Denominación Pagador Servicio', size=250)

    ###############################################
    ########## ITEMS ##########
    gre_unidad_de_medida = fields.Selection([
        ('NIU', 'PRODUCTO'),
        ('ZZ', 'SERVICIO')
        ],
        string="Unidad de medida para SUNAT", default='NIU')
    
    ## OPTIONAL
    # codigo = fields.Char(string='Código interno del producto o servicio, asignado internamente.', size=250)
    # codigo_dam = fields.Char(string='Para traslado exportación o importación.', size=23) 
    
    ########## DOCUMENTO ##########
    gre_tipo = fields.Selection([
        ('01', 'Factura'),
        ('03', 'Boleta de Venta'),
        ('09', 'Guía de Remisión Remitente'),
        ('31', 'Guía de Remisión Transportista')
        ],
        string="Documento/comprobante", default='01')
    gre_account_move_ids = fields.Many2many(comodel_name='account.move', string='Facturas Asociadas')
    

    ######### RESPUESTA REQUEST #########
    gre_respuesta = fields.Json(string="Respuesta de la Solicitud")
    gre_respuesta_error4 = fields.Json(string="Error de cliente")
    gre_enlace = fields.Char(string="URL a la GRE")
    gre_pdf_zip_base64 = fields.Binary(string="PDF de la GRE en binario")

    gre_aceptada_por_sunat = fields.Boolean(string="GRE aceptada por SUNAT")


    @api.depends('gre_serie', 'gre_numero')
    def _compute_doc_name(self):
        for rec in self:
            serie = rec.gre_serie or ''
            numero = str(rec.gre_numero).zfill(8) if rec.gre_numero else ''
            rec.gre_doc_name = f"{serie}-{numero}" if (serie and numero) else ''

    @api.depends('partner_id')
    def _compute_ubigeo_llegada(self):
        for rec in self:
            if (rec.partner_id.state_id and rec.partner_id.city_id and rec.partner_id.l10n_pe_district):
                department = rec.env['pe.department'].search([("name" , "=", rec.partner_id.state_id.name.upper())], limit=1) 
                province = rec.env['pe.province'].search([("name" , "=", rec.partner_id.city_id.name.upper()), ("department_id", "=", department.id)], limit=1) 
                district = rec.env['pe.district'].search([("name" , "=", rec.partner_id.l10n_pe_district.name.upper()), ("department_id", "=", department.id), ("province_id", "=", province.id)], limit=1) 
                
                if district:
                    rec.gre_punto_de_llegada_ubigeo = district.code
                    
                else:
                    rec.gre_punto_de_llegada_ubigeo = ''
            
    
    @api.depends('partner_id')
    def _compute_ubigeo_partida(self):
        for rec in self:
            if (rec.partner_id.state_id and rec.partner_id.city_id and rec.partner_id.l10n_pe_district):
                department = rec.env['pe.department'].search([("name" , "=", rec.partner_id.state_id.name.upper())], limit=1) 
                province = rec.env['pe.province'].search([("name" , "=", rec.partner_id.city_id.name.upper()), ("department_id", "=", department.id)], limit=1) 
                district = rec.env['pe.district'].search([("name" , "=", rec.partner_id.l10n_pe_district.name.upper()), ("department_id", "=", department.id), ("province_id", "=", province.id)], limit=1) 
                
                if district:
                    rec.gre_punto_de_partida_ubigeo = district.code
                    
                else:
                    rec.gre_punto_de_partida_ubigeo = ''

            
    @api.model
    def create(self, vals):
        _logger.info(f"\n\n\n\n --------------- {vals.get('gre_serie')}, {vals.get('gre_numero')}  --------------- \n\n\n\n")

        if not vals.get('gre_serie'):
            vals['gre_serie'] = self._fields['gre_serie'].default(self)
        
        if not vals.get('gre_numero'):
            _logger.info("\n\n\n\n +++++++++++++++++++++++++ \n\n\n\n")
            last = self.search([('gre_serie', '=', vals['gre_serie']), ('gre_numero', '!=', False)], order='gre_numero desc', limit=1)
            next_num = (last.gre_numero or 0) + 1
            if next_num > 99999999:
                raise ValidationError("Max limit of digits for this serie has been reached.")

            _logger.info(f"\n\n\n\n {self.gre_numero}, {next_num} \n\n\n\n")
            vals['gre_numero'] = next_num
        
        return super().create(vals)

    @api.onchange('picking_type_id')
    def _onchange_picking_type_for_outgoing(self):
        if self.picking_type_id:
            if self.picking_type_id.code == 'outgoing':
                self.is_outgoing = True
            elif self.picking_type_id.code == 'internal':
                self.is_outgoing = False

    @api.onchange('partner_id')
    def _onchange_contacto_id(self):
        if self.partner_id:
            self.gre_destinatario_documento_numero = self.partner_id.vat
            self.gre_destinatario_denominacion = self.partner_id.name
            self.gre_punto_de_llegada_direccion = self.partner_id.street
            self.gre_punto_de_llegada_ubigeo = self.partner_id.zip
            
    @api.onchange('gre_driver_employee_id')
    def _onchange_driver_employee_id(self):
        if self.gre_driver_employee_id:
            if self.gre_driver_employee_id.partner_id:
                self.gre_conductor_documento_numero = self.gre_driver_employee_id.partner_id.vat or self.gre_driver_employee_id.identification_id
                self.gre_conductor_denominacion = self.gre_driver_employee_id.partner_id.name
                self.gre_conductor_numero_licencia = self.gre_driver_employee_id.driving_license_number

    @api.onchange('gre_conductor_denominacion')
    def _onchange_conductor_denominacion(self):
        if self.gre_conductor_denominacion:
            split_denomination = self.gre_conductor_denominacion.split(',')
            if not len(split_denomination) == 2:
                pass
            else:
                nombre, apellido = split_denomination
                self.gre_conductor_nombre = nombre.strip()
                self.gre_conductor_apellidos = apellido.strip()

    # @api.constrains('account_move_ids')
    # def _check_serie_numero_existance(self):
    #     if self.gre_account_move_ids:
    #         if not self.gre_account_move_ids.l10n_pe_in_edi_serie or not self.gre_account_move_ids.l10n_pe_in_edi_number:
    #             raise UserError("La serie y el número deben existir para todas las facturas")
            
    # @api.constrains('serie', 'tipo_de_comprobante')
    # def _check_serie_format(self):
    #     for record in self:
    #         if record.tipo_de_comprobante == '7' and not record.serie.startswith('T'):
    #             raise UserError("Para GRE Remitente, la serie debe empezar con 'T'.")
    #         if record.tipo_de_comprobante == '8' and not record.serie.startswith('V'):
    #             raise UserError("Para GRE Transportista, la serie debe empezar con 'V'.")

    # @api.constrains('numero')
    # def _check_numero_length(self):
    #     for record in self:
    #         if record.numero and len(str(record.numero)) > 8:
    #             raise UserError("El número debe tener como máximo 8 dígitos.")

    # @api.constrains('peso_bruto_total')
    # def _check_peso_bruto(self):
    #     for record in self:
    #         if record.peso_bruto_total <= 0:
    #             raise UserError("El peso bruto total debe ser mayor a 0.")

    # @api.constrains('tipo_de_comprobante', 'destinatario_documento_tipo', 'destinatario_documento_numero', 'destinatario_denominacion')
    # def _check_destinatario(self):
    #     for record in self:
    #         if record.tipo_de_comprobante == '8':
    #             if not record.destinatario_documento_tipo or not record.destinatario_documento_numero or not record.destinatario_denominacion:
    #                 raise UserError("Para GRE Transportista, los datos del destinatario son obligatorios.")
                

    # @api.constrains('cliente_email', 'cliente_email_1', 'cliente_email_2')
    # def _check_email_format(self):
    #     email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    #     for record in self:
    #         for email in [record.cliente_email, record.cliente_email_1, record.cliente_email_2]:
    #             if email and not re.match(email_regex, email):
    #                 raise UserError("El formato del email es inválido.")

    # @api.constrains('motivo_de_traslado', 'motivo_de_traslado_otros_descripcion')
    # def _check_motivo_otros(self):
    #     for record in self:
    #         if record.motivo_de_traslado == '13' and not record.motivo_de_traslado_otros_descripcion:
    #             raise UserError("Para motivo de traslado 'OTROS', debe proporcionar la descripción.")

    # @api.constrains('motivo_de_traslado', 'documento_relacionado_codigo')
    # def _check_documento_relacionado(self):
    #     for record in self:
    #         if record.motivo_de_traslado in ['08', '09'] and not record.documento_relacionado_codigo:
    #             raise UserError("Para importación o exportación, debe proporcionar el código de documento relacionado.")


    # @api.constrains('numero_de_bultos')
    # def _check_numero_bultos(self):
    #     for record in self:
    #         if record.numero_de_bultos <= 0:
    #             raise UserError("El número de bultos debe ser mayor a 0.")

    # @api.constrains('tipo_de_transporte', 'transportista_documento_tipo', 'transportista_documento_numero', 'transportista_denominacion')
    # def _check_transportista(self):
    #     for record in self:
    #         if record.tipo_de_transporte == '01':
    #             if not record.transportista_documento_tipo or not record.transportista_documento_numero or not record.transportista_denominacion:
    #                 raise UserError("Para transporte público, los datos del transportista son obligatorios.")

    # @api.constrains('tipo_de_transporte', 'conductor_documento_tipo', 'conductor_documento_numero', 'conductor_denominacion', 'conductor_nombre', 'conductor_apellidos', 'conductor_numero_licencia')
    # def _check_conductor(self):
    #     for record in self:
    #         if record.tipo_de_transporte == '02':
    #             if not all([record.conductor_documento_tipo, record.conductor_documento_numero, record.conductor_denominacion, record.conductor_nombre, record.conductor_apellidos, record.conductor_numero_licencia]):
    #                 raise UserError("Para transporte privado, los datos del conductor son obligatorios.")


    # @api.constrains('sunat_envio_indicador', 'subcontratador_documento_tipo', 'subcontratador_documento_numero', 'subcontratador_denominacion')
    # def _check_subcontratador(self):
    #     for record in self:
    #         if record.sunat_envio_indicador == '02':
    #             if not record.subcontratador_documento_tipo or not record.subcontratador_documento_numero or not record.subcontratador_denominacion:
    #                 raise UserError("Para indicador de envío '02', los datos del subcontratador son obligatorios.")

    # @api.constrains('sunat_envio_indicador', 'pagador_servicio_documento_tipo_identidad', 'pagador_servicio_documento_numero_identidad', 'pagador_servicio_denominacion')
    # def _check_pagador_servicio(self):
    #     for record in self:
    #         if record.sunat_envio_indicador == '03':
    #             if not record.pagador_servicio_documento_tipo_identidad or not record.pagador_servicio_documento_numero_identidad or not record.pagador_servicio_denominacion:
    #                 raise UserError("Para indicador de envío '03', los datos del pagador del servicio son obligatorios.")

    # @api.constrains('motivo_de_traslado', 'punto_de_partida_codigo_establecimiento_sunat', 'punto_de_llegada_codigo_establecimiento_sunat')
    # def _check_codigo_establecimiento(self):
    #     for record in self:
    #         if record.motivo_de_traslado in ['04', '18']:
    #             if not record.punto_de_partida_codigo_establecimiento_sunat or not record.punto_de_llegada_codigo_establecimiento_sunat:
    #                 raise UserError("Para traslado entre establecimientos, el código de establecimiento SUNAT es obligatorio.")

    def action_send_request(self):
        for rec in self:
            ## Existencia de todos los campos necesarios
            fields_strings = {
                "gre_operacion": self._fields["gre_operacion"].string,
                "gre_tipo_de_comprobante": self._fields["gre_tipo_de_comprobante"].string,
                "gre_serie": self._fields["gre_serie"].string,
                #gre_ "numero": self._fields["numero"].string,

                "gre_cliente_tipo_de_documento": self._fields["gre_cliente_tipo_de_documento"].string,
                "gre_cliente_numero_de_documento": self._fields["gre_cliente_numero_de_documento"].string,
                "gre_cliente_denominacion": self._fields["gre_cliente_denominacion"].string,
                "gre_cliente_direccion": self._fields["gre_cliente_direccion"].string,

                "gre_fecha_de_emision": self._fields["gre_fecha_de_emision"].string,
                "gre_fecha_de_inicio_de_traslado": self._fields["gre_fecha_de_inicio_de_traslado"].string,
                # "enviar_automaticamente_al_cliente": self._fields["enviar_automaticamente_al_cliente"].string,

                "gre_peso_bruto_total": self._fields["gre_peso_bruto_total"].string,
                "gre_peso_bruto_unidad_de_medida": self._fields["gre_peso_bruto_unidad_de_medida"].string,

                "gre_punto_de_partida_ubigeo": self._fields["gre_punto_de_partida_ubigeo"].string,
                "gre_punto_de_partida_direccion": self._fields["gre_punto_de_partida_direccion"].string,

                "gre_punto_de_llegada_ubigeo": self._fields["gre_punto_de_llegada_ubigeo"].string,
                "gre_punto_de_llegada_direccion": self._fields["gre_punto_de_llegada_direccion"].string,

                "gre_transportista_placa_numero": self._fields["gre_transportista_placa_numero"].string,

                "gre_conductor_documento_tipo": self._fields["gre_conductor_documento_tipo"].string,
                # "driver_employee_id": self._fields["driver_employee_id"].string,
                "gre_conductor_documento_numero": self._fields["gre_conductor_documento_numero"].string,
                "gre_conductor_denominacion": self._fields["gre_conductor_denominacion"].string,
                "gre_conductor_nombre": self._fields["gre_conductor_nombre"].string,
                "gre_conductor_apellidos": self._fields["gre_conductor_apellidos"].string,
                "gre_conductor_numero_licencia": self._fields["gre_conductor_numero_licencia"].string,

                "gre_destinatario_documento_tipo": self._fields["gre_destinatario_documento_tipo"].string,
                "gre_destinatario_documento_numero": self._fields["gre_destinatario_documento_numero"].string,
                "gre_destinatario_denominacion": self._fields["gre_destinatario_denominacion"].string,

                "gre_unidad_de_medida": self._fields["gre_unidad_de_medida"].string,
                "gre_tipo": self._fields["gre_tipo"].string,
                "gre_account_move_ids": self._fields["gre_account_move_ids"].string
            }

            non_completed_fields = []
            for field in fields_strings:
                if not self[field]:
                    non_completed_fields.append(field)
                
            if non_completed_fields:
                error_message = "Campo(s) no completado(s) para la GRE: \n"
                for field_to_complete in non_completed_fields:
                    error_message += f"-> {fields_strings[field_to_complete]}\n"
                raise ValidationError(error_message)


            ## Check existencia de serie y número de documento (factura)
            if self.gre_account_move_ids:
                for account_move in self.gre_account_move_ids:
                    if account_move.sequence_number == 0:
                        raise UserError("La serie y el número deben existir para todas las facturas")

            ## Check existencia de items
            if self.move_ids_without_package:
                for move in self.move_ids_without_package:
                    if not move.description_picking:
                        raise UserError("Todos los ítems deben tener descripciones.")
            else:
                raise UserError("Debe agregar ítems para generar la GRE.")
                     
            
            ## Check formato de serie (registro)
            if rec.gre_tipo_de_comprobante and rec.gre_serie:
                if rec.gre_tipo_de_comprobante == '7' and not rec.gre_serie.startswith('T'):
                    raise UserError("Para GRE Remitente, la serie debe empezar con 'T'.")
                if rec.gre_tipo_de_comprobante == '8' and not rec.gre_serie.startswith('V'):
                    raise UserError("Para GRE Transportista, la serie debe empezar con 'V'.")

            ## Check formato de numero (registro):
            if rec.gre_numero:  
                if rec.gre_numero and len(str(rec.gre_numero)) > 8:
                    raise UserError("El número debe tener como máximo 8 dígitos.")

            ## Check peso bruto
            if rec.gre_peso_bruto_total:
                if rec.gre_peso_bruto_total <= 0:
                    raise UserError("El peso bruto total debe ser mayor a 0.")

            ## Check datos destinatario
            if rec.gre_tipo_de_comprobante:
                if rec.gre_tipo_de_comprobante == '8':
                    if not rec.gre_destinatario_documento_tipo or not rec.gre_destinatario_documento_numero or not rec.gre_destinatario_denominacion:
                        raise UserError("Para GRE Transportista, los datos del destinatario son obligatorios.")

            ## Check formato licencia conductor
            if rec.gre_conductor_numero_licencia:
                if len(rec.gre_conductor_numero_licencia) < 9:
                    raise ValidationError("El número de licencia del conductor debe tener de 9 a 10 caracteres.")

            ## Check formato ubigeo
            if rec.gre_punto_de_llegada_ubigeo:
                if len(rec.gre_punto_de_llegada_ubigeo) != 6:
                    raise ValidationError("El ubigeo (punto de llegada) debe contener 6 caracteres.")
                else:
                    if not self.env['pe.district'].search_count([('code', '=', rec.gre_punto_de_llegada_ubigeo)]):
                        raise ValidationError(f"El ubigeo (llegada) {rec.gre_punto_de_llegada_ubigeo} no existe. Corregir.")
            
            if rec.gre_punto_de_partida_ubigeo:
                if len(rec.gre_punto_de_partida_ubigeo) != 6:
                    raise ValidationError("El ubigeo (punto de partida) debe contener 6 caracteres.")
                else:
                    if not self.env['pe.district'].search_count([('code', '=', rec.gre_punto_de_partida_ubigeo)]):
                        raise ValidationError(f"El ubigeo (partida) {rec.gre_punto_de_partida_ubigeo} no existe. Corregir.")

            ## Check formato plata_conductor
            if rec.gre_transportista_placa_numero:
                if "-" in rec.gre_transportista_placa_numero or (len(rec.gre_transportista_placa_numero) > 8 or len(rec.gre_transportista_placa_numero) < 6):
                    raise ValidationError("El número de placa no debe contener guión (-) y debe tener de 6 a 8 caracteres.") 


            items = [
                {"unidad_de_medida": "NIU",
                 "codigo": move.product_id.product_tmpl_id.default_code,
                 "descripcion": move.description_picking,
                 "cantidad": str(move.quantity)
                 }
                 for move  in self.move_ids_without_package
            ]
            documentos_relacionados = [
                {"tipo": account_move.l10n_latam_document_type_id.code,
                 "serie": account_move.l10n_latam_document_type_id.doc_code_prefix + "001",
                 "numero": account_move.sequence_number
                 } 
                 for account_move in self.gre_account_move_ids
            ]

            payload = {
                "operacion": self.gre_operacion,
                "tipo_de_comprobante": int(self.gre_tipo_de_comprobante),
                "serie": self.gre_serie,
                "numero": str(self.gre_numero),
                "cliente_tipo_de_documento": int(self.gre_cliente_tipo_de_documento),
                "cliente_numero_de_documento": self.gre_cliente_numero_de_documento,
                "cliente_denominacion": self.gre_cliente_denominacion,
                "cliente_direccion": self.gre_cliente_direccion,
                "fecha_de_emision": self.gre_fecha_de_emision.strftime("%d-%m-%Y"),
                "peso_bruto_total": str(self.gre_peso_bruto_total),
                "peso_bruto_unidad_de_medida": self.gre_peso_bruto_unidad_de_medida,
                "fecha_de_inicio_de_traslado": self.gre_fecha_de_inicio_de_traslado.strftime("%d-%m-%Y"),
                "transportista_placa_numero": self.gre_transportista_placa_numero.upper(),
                "conductor_documento_tipo": self.gre_conductor_documento_tipo,
                "conductor_documento_numero": self.gre_conductor_documento_numero,
                "conductor_denominacion": self.gre_conductor_denominacion,
                "conductor_nombre": self.gre_conductor_nombre.upper(),
                "conductor_apellidos": self.gre_conductor_apellidos.upper(),
                "conductor_numero_licencia": self.gre_conductor_numero_licencia,
                "destinatario_documento_tipo": self.gre_destinatario_documento_tipo,
                "destinatario_documento_numero": self.gre_destinatario_documento_numero,
                "destinatario_denominacion": self.gre_destinatario_denominacion,
                "punto_de_partida_ubigeo": self.gre_punto_de_partida_ubigeo,
                "punto_de_partida_direccion": self.gre_punto_de_partida_direccion,
                "punto_de_llegada_ubigeo": self.gre_punto_de_llegada_ubigeo,
                "punto_de_llegada_direccion": self.gre_punto_de_llegada_direccion,
                "enviar_automaticamente_al_cliente": str(self.gre_enviar_automaticamente_al_cliente).lower(),
                "items": items,
                "documento_relacionado": documentos_relacionados
            }

            _logger.info(f"PAYLOAD\n\t{json.dumps(payload)}\n\n")

            ruta = self.env['l10n_pe_edi.shop'].sudo().search([("partner_id", "=", self.company_id.partner_id.id)], limit=1).l10n_pe_edi_ose_url
            token = self.env['l10n_pe_edi.shop'].sudo().search([("partner_id", "=", self.company_id.partner_id.id)], limit=1).l10n_pe_edi_ose_token

            if not ruta:
                raise UserError(f"No se encontró la URL nubefact para {self.company_id.partner_id.name}.")
            if not token: 
                raise UserError(f"No se encontró el token nubefact para {self.company_id.partner_id.name}.")

            headers = {
                "Authorization": f"Token token={token}",
                "Content-Type": "application/json"
            }

            try:
                response = requests.post(
                    ruta,
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=10
                )
                response.raise_for_status()
                rec.gre_respuesta = response.json()

                rec.gre_aceptada_por_sunat = rec.gre_respuesta['aceptada_por_sunat']             
                rec.gre_enlace = rec.gre_respuesta['enlace'] or False
                rec.gre_pdf_zip_base64 = rec.gre_respuesta['pdf_zip_base64'] or False
                
                respuesta_string = json.dumps(rec.gre_respuesta, ensure_ascii=False, indent=2)


                _logger.info(f"\n\n\n\n{respuesta_string}\n\n\n\n")
                if rec.gre_aceptada_por_sunat:
                    return {
                        'effect': {
                            'fadeout': 'slow',
                            'message': '¡Guía aceptada por SUNAT!',
                            'type': 'rainbow_man',
                        }
                    }
                
                # else:
                #     self.env.user.notify_warning(message="Guía no fue aceptada por SUNAT!")


            except Exception as e:
                rec.gre_respuesta_error4 = response.json()
                _logger.info("\nError: ", response.text)
                _logger.info(f"\nError:  {str(e)}\n")
                raise ValidationError(rec.gre_respuesta_error4['errors'])

    def action_print_pdf(self):
        self.ensure_one()
        if not self.gre_pdf_zip_base64:
            raise UserError("No hay PDF disponible para imprimir.")
        return {
        'type': 'ir.actions.act_url',
        'url': f'/web/content?model=stock.picking&id={self.id}&field=gre_pdf_zip_base64&download=true&filename={self.gre_doc_name}.pdf',
        'target': 'new',
        }

    def action_open_url(self):
        self.ensure_one()
        if not self.gre_enlace:
            raise UserError("No hay enlace disponible.")
        
        url = self.gre_enlace + ".pdf"
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
    

    def action_consult_gre(self):
        self.ensure_one()
        token = self.env['l10n_pe_edi.shop'].sudo().search([("partner_id", "=", self.company_id.partner_id.id)], limit=1).l10n_pe_edi_ose_token
        ruta = self.env['l10n_pe_edi.shop'].sudo().search([("partner_id", "=", self.company_id.partner_id.id)], limit=1).l10n_pe_edi_ose_url

        headers = {
            "Authorization": f"Token token={token}",
            "Content-Type": "application/json"
        }

        # Consultar guía
        try:
            response = requests.post(
                ruta,
                headers=headers,
                data=json.dumps({
                    "operacion": "consultar_guia",
                    "tipo_de_comprobante": 8,
                    "serie": "VVV1",
                    "numero": self.gre_numero
                    }
                ),
                timeout=10
            )
            response.raise_for_status()
            _logger.info(f"\n\n\n\n{response.text}\n\n\n\n")

            self.gre_enlace = response.json()['enlace'] or False
            self.gre_pdf_zip_base64 = response.json()['pdf_zip_base64'] or False
            
        except Exception as e:

            _logger.info("\nError: ", response.text)
            _logger.info(f"\nError:  {str(e)}\n")
                
            