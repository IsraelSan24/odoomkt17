from odoo import fields, models, api, _
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
    gre_serie = fields.Char(string='Serie', size=4, compute='_compute_default_serie', store=True, readonly=False)
    gre_numero = fields.Integer(string='Número')
    
    gre_cliente_tipo_de_documento = fields.Selection(
        [('6', 'RUC'), 
         ('1', 'DNI'), 
         ('4', 'CARNET DE EXTRANJERÍA'), 
         ('7', 'PASAPORTE'), 
         ('A', 'CÉDULA DIPLOMÁTICA'), 
         ('0', 'NO DOMICILIADO')], 
         string='Tipo de Documento del Cliente', default='6')

    gre_cliente_id = fields.Many2one("res.partner", string="Cliente", help="Destinatario (GRE Remitente) o Remitente (GRE Transportista).")
    gre_cliente_numero_de_documento = fields.Char(string='Número de Documento', size=15)
    gre_cliente_denominacion = fields.Char(string='Denominación', size=100, help="Razón o nombre completo del cliente.")
    gre_cliente_direccion = fields.Char(string='Dirección', size=100)

    gre_fecha_de_emision = fields.Date(string='Fecha de Emisión', default=lambda self: self.scheduled_date)
    gre_fecha_de_inicio_de_traslado = fields.Date(string='Fecha de Inicio de Traslado', default=lambda self: self.scheduled_date)
    gre_enviar_automaticamente_al_cliente = fields.Boolean(string='Enviar Automáticamente al Cliente', default=False, help="Se envía sólo si la GRE fue aceptada por la Sunat.")
    
    gre_peso_bruto_total = fields.Float(string='Peso Bruto Total', digits=(12, 10))
    gre_peso_bruto_unidad_de_medida = fields.Selection(
        [('KGM', 'Kilogramos'), 
         ('TNE', 'Toneladas')], 
         string='Unidad de Medida Peso')
    
    gre_punto_de_partida_ubigeo = fields.Char(string='Ubigeo Punto de Partida', size=6, compute="_compute_ubigeo_partida", store=True, readonly=False)
    gre_punto_de_partida_direccion = fields.Char(string='Dirección Punto de Partida', size=150)
    gre_punto_de_partida_departamento = fields.Many2one("pe.department", default=lambda self: self.env['pe.department'].search([('code', '=', '15')], limit=1))
    gre_punto_de_partida_provincia = fields.Many2one("pe.province", default=lambda self: self.env['pe.province'].search([('code', '=', '1501')], limit=1))
    gre_punto_de_partida_distrito = fields.Many2one("pe.district")

    gre_punto_de_llegada_ubigeo = fields.Char(string='Ubigeo Punto de Llegada', size=6, compute="_compute_ubigeo_llegada", store=True, readonly=False)
    gre_punto_de_llegada_direccion = fields.Char(string='Dirección Punto de Llegada', size=150)
    gre_punto_de_llegada_departamento = fields.Many2one("pe.department", default=lambda self: self.env['pe.department'].search([('code', '=', '15')], limit=1))
    gre_punto_de_llegada_provincia = fields.Many2one("pe.province", default=lambda self: self.env['pe.province'].search([('code', '=', '1501')], limit=1))
    gre_punto_de_llegada_distrito = fields.Many2one("pe.district")

    gre_transportista_placa_numero = fields.Char(string='Placa Número Transportista', size=8)


    ########## CONDUCTOR (OBLIGATORIO PARA AMBOS TIPOS SEGÚN CONDICIONES) ##########
    gre_conductor_documento_tipo = fields.Selection(
        [('1', 'DNI'), 
         ('4', 'CARNET DE EXTRANJERÍA'), 
         ('7', 'PASAPORTE'), 
         ('A', 'CÉDULA DIPLOMÁTICA'), 
         ('0', 'NO DOMICILIADO')], 
         string='Tipo Documento Conductor', default='1')
    
    gre_driver_employee_id = fields.Many2one('hr.employee', string="Empleado transportista", domain=[('job_id.name', 'in', ['TRANSPORTISTA', 'CONDUCTOR'])])
    gre_conductor_documento_numero = fields.Char(string='Número Documento Conductor', size=15)
    gre_conductor_denominacion = fields.Char(string='Denominación Conductor', size=100, help="Razón o nombre completo del conductor.")
    gre_conductor_nombre = fields.Char(string='Nombre Conductor', size=250)
    gre_conductor_apellidos = fields.Char(string='Apellidos Conductor', size=250)
    gre_conductor_numero_licencia = fields.Char(string='Número Licencia Conductor', size=10)

    ########## SOLO TRANSPORTISTA ##########
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
    gre_motivo_de_traslado = fields.Selection(
        [('01', 'VENTA'), 
         ('14', 'VENTA SUJETA A CONFIRMACION DEL COMPRADOR'), 
         ('02', 'COMPRA'), 
         ('04', 'TRASLADO ENTRE ESTABLECIMIENTOS DE LA MISMA EMPRESA'), 
         ('18', 'TRASLADO EMISOR ITINERANTE CP'), 
         ('08', 'IMPORTACION'), 
         ('09', 'EXPORTACION'), 
         ('13', 'OTROS'), 
         ('05', 'CONSIGNACION'), 
         ('17', 'TRASLADO DE BIENES PARA TRANSFORMACION'), 
         ('03', 'VENTA CON ENTREGA A TERCEROS'), 
         ('06', 'DEVOLUCION'), 
         ('07', 'RECOJO DE BIENES TRANSFORMADOS')], 
         string='Motivo de Traslado')
    
    gre_motivo_de_traslado_otros_descripcion = fields.Char(string='Descripción Otros Motivo', size=70)
    gre_documento_relacionado_codigo = fields.Char(string='Código Documento Relacionado (DAM/DS)', size=23)
    gre_numero_de_bultos = fields.Float(string='Número de Bultos', digits=(6, 0))
    
    gre_tipo_de_transporte = fields.Selection(
        [('01', 'TRANSPORTE PÚBLICO'), 
         ('02', 'TRANSPORTE PRIVADO')], 
         string='Tipo de Transporte')
    
    gre_transportista_documento_tipo = fields.Selection([('6', 'RUC')], string='Tipo Documento Transportista', default='6')
    gre_transportista_documento_numero = fields.Char(string='Número Documento Transportista', size=11)
    gre_transportista_denominacion = fields.Char(string='Denominación Transportista', size=100)
    
    gre_punto_de_partida_codigo_establecimiento_sunat = fields.Char(string='Código Establecimiento SUNAT Partida', size=4)
    gre_punto_de_llegada_codigo_establecimiento_sunat = fields.Char(string='Código Establecimiento SUNAT Llegada', size=4)

    ## OPTIONAL
    gre_tuc_vehiculo_principal = fields.Char(string='Certificado de Habilitación Vehicular', size=15)
    gre_mtc = fields.Char(string='Número de Registro MTC', default="15171560CNG", size=20)
    gre_observacion = fields.Char(string='Observación', size=1000)

    ###############################################
    ########## ITEMS ##########
    gre_unidad_de_medida = fields.Selection([
        ('NIU', 'PRODUCTO'),
        ('ZZ', 'SERVICIO')
        ],
        string="Unidad de medida para SUNAT", default='NIU')
    
    ########## DOCUMENTO ##########
    gre_tipo_documento = fields.Selection([
        ('01', 'Factura'),
        ('03', 'Boleta de Venta'),
        ('09', 'Guía de Remisión Remitente'),
        ('31', 'Guía de Remisión Transportista')
        ],
        string="Documento/comprobante")
    gre_account_move_id = fields.Many2one(comodel_name='account.move', string='Factura Asociada')
    gre_documento_serie = fields.Char(string="Serie del Documento Relacionado", size=4)
    gre_documento_numero = fields.Integer(string="Número del Documento Relacionado", help="Correlativo, sin ceros a la izquierda.")


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
    
    @api.depends('gre_tipo_de_comprobante')
    def _compute_default_serie(self):
        for rec in self:
            if rec.gre_tipo_de_comprobante == '7':
                rec.gre_serie = 'TTT1'
            elif rec.gre_tipo_de_comprobante == '8':
                rec.gre_serie = 'VVV1'
            else:
                rec.gre_serie = False
    
    @api.depends('gre_punto_de_partida_distrito')
    def _compute_ubigeo_partida(self):
        for rec in self:
            if (rec.gre_punto_de_partida_departamento and rec.gre_punto_de_partida_provincia and rec.gre_punto_de_partida_distrito):
                rec.gre_punto_de_partida_ubigeo = rec.gre_punto_de_partida_distrito.code
            else:
                rec.gre_punto_de_partida_ubigeo = ''

    @api.depends('gre_punto_de_llegada_distrito')
    def _compute_ubigeo_llegada(self):
        for rec in self:
            if (rec.gre_punto_de_llegada_departamento and rec.gre_punto_de_llegada_provincia and rec.gre_punto_de_llegada_distrito):
                rec.gre_punto_de_llegada_ubigeo = rec.gre_punto_de_llegada_distrito.code
            else:
                rec.gre_punto_de_llegada_ubigeo = ''
            
    @api.model
    def create(self, vals):
        if not vals.get('gre_serie'):
            tipo_comp = vals.get('gre_tipo_de_comprobante', '8')
            vals['gre_serie'] = 'TTT1' if tipo_comp == '7' else 'VVV1'
        
        if not vals.get('gre_numero'):
            _logger.info("\n\n\n\n +++++++++++++++++++++++++ \n\n\n\n")
            # last = self.search([('gre_serie', '=', vals['gre_serie']), ('gre_numero', '!=', False)], order='gre_numero desc', limit=1)
            last = self.search([('gre_numero', '!=', False)], order='gre_numero desc', limit=1)
            next_num = (last.gre_numero or 0) + 1
            if next_num > 99999999:
                raise ValidationError("Max limit of digits for this serie has been reached.")

            _logger.info(f"\n\n\n\n {self.gre_numero}, {next_num} \n\n\n\n")
            vals['gre_numero'] = next_num
        
        if vals.get('gre_doc_name') and isinstance(vals['gre_doc_name'], str):
            vals['gre_doc_name'] = vals['gre_doc_name'].strip()

        return super().create(vals)

    @api.onchange('gre_punto_de_partida_departamento')
    def _onchange_gre_punto_de_partida_departamento(self):
        if self.gre_punto_de_partida_departamento:
            self.gre_punto_de_partida_provincia = False
            self.gre_punto_de_partida_distrito = False

    @api.onchange('gre_punto_de_llegada_departamento')
    def _onchange_gre_punto_de_llegada_departamento(self):
        if self.gre_punto_de_llegada_departamento:
            self.gre_punto_de_llegada_provincia = False
            self.gre_punto_de_llegada_distrito = False

    @api.onchange('gre_punto_de_partida_provincia')
    def _onchange_gre_punto_de_partida_provincia(self):
        if self.gre_punto_de_partida_provincia:
            self.gre_punto_de_partida_distrito = False

    @api.onchange('gre_punto_de_llegada_provincia')
    def _onchange_gre_punto_de_llegada_provincia(self):
        if self.gre_punto_de_llegada_provincia:
            self.gre_punto_de_llegada_distrito = False

    @api.onchange('gre_cliente_id')
    def _onchange_gre_cliente_id(self):
        label_to_value = {label: value for value, label in self._fields['gre_cliente_tipo_de_documento'].selection}

        if self.gre_cliente_id:
            tipo_doc_name = self.gre_cliente_id.l10n_latam_identification_type_id.name
            tipo_doc_value = label_to_value.get(tipo_doc_name)

            self.gre_cliente_tipo_de_documento = tipo_doc_value or False
            self.gre_cliente_numero_de_documento = self.gre_cliente_id.vat
            self.gre_cliente_denominacion = self.gre_cliente_id.name
            self.gre_cliente_direccion = self.gre_cliente_id.street

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
            # Para GRE Transportista: partner es destinatario
            # Para GRE Remitente: partner es destinatario también
            self.gre_destinatario_documento_numero = self.partner_id.vat
            self.gre_destinatario_denominacion = self.partner_id.name
            self.gre_punto_de_llegada_direccion = self.partner_id.street
            
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

    def action_send_request(self):
        ruta = self.env['l10n_pe_edi.shop'].sudo().search([("partner_id", "=", self.company_id.partner_id.id)], limit=1).l10n_pe_edi_ose_url
        token = self.env['l10n_pe_edi.shop'].sudo().search([("partner_id", "=", self.company_id.partner_id.id)], limit=1).l10n_pe_edi_ose_token
        
        for rec in self:
            ## Validaciones comunes para ambos tipos
            self._validate_common_fields(rec)
            
            ## Validaciones específicas según tipo
            if rec.gre_tipo_de_comprobante == '7':
                self._validate_remitente_fields(rec)
            elif rec.gre_tipo_de_comprobante == '8':
                self._validate_transportista_fields(rec)

            ## Construir payload
            payload = self._build_payload(rec)
            
            _logger.info(f"PAYLOAD\n\t{json.dumps(payload)}\n\n")

            if not ruta:
                raise UserError(f"No se encontró la URL nubefact para {rec.company_id.partner_id.name}.")
            if not token: 
                raise UserError(f"No se encontró el token nubefact para {rec.company_id.partner_id.name}.")

            headers = {
                "Authorization": f"Token token={token}",
                "Content-Type": "application/json"
            }

            # response = None

            try:
                response = requests.post(
                    ruta,
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=10
                )
                response.raise_for_status()
                rec.gre_respuesta = response.json()

                rec.gre_aceptada_por_sunat = rec.gre_respuesta.get('aceptada_por_sunat', False)             
                rec.gre_enlace = rec.gre_respuesta.get('enlace', False)
                rec.gre_pdf_zip_base64 = rec.gre_respuesta.get('pdf_zip_base64', False)
                
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

            except Exception as e:
                rec.gre_respuesta_error4 = response.json()
                _logger.info("\nError: ", response.text)
                _logger.info(f"\nError:  {str(e)}\n")
                # raise ValidationError(str(e))
                if rec.gre_respuesta_error4.get('errors', False):
                    raise ValidationError(rec.gre_respuesta_error4.get('errors'))
                elif rec.gre_respuesta_error4.get('error', False):
                    raise ValidationError(rec.gre_respuesta_error4.get('error'))


    def _validate_common_fields(self, rec):
        """Validaciones comunes para ambos tipos de GRE"""
        fields_strings = {
            "gre_operacion": "Operación",
            "gre_tipo_de_comprobante": "Tipo de Comprobante",
            "gre_serie": "Serie",
            "gre_numero": "Número",
            "gre_cliente_tipo_de_documento": "Tipo Documento Cliente",
            "gre_cliente_numero_de_documento": "Número Documento Cliente",
            "gre_cliente_denominacion": "Denominación Cliente",
            "gre_cliente_direccion": "Dirección Cliente",
            "gre_fecha_de_emision": "Fecha de Emisión",
            "gre_fecha_de_inicio_de_traslado": "Fecha Inicio Traslado",
            "gre_peso_bruto_total": "Peso Bruto Total",
            "gre_peso_bruto_unidad_de_medida": "Unidad Medida Peso",
            "gre_punto_de_partida_departamento": "Departamento Partida",
            "gre_punto_de_partida_provincia": "Provincia Partida",
            "gre_punto_de_partida_distrito": "Distrito Partida",
            "gre_punto_de_partida_direccion": "Dirección Partida",
            "gre_punto_de_llegada_departamento": "Departamento Llegada",
            "gre_punto_de_llegada_provincia": "Provincia Llegada",
            "gre_punto_de_llegada_distrito": "Distrito Llegada",
            "gre_punto_de_llegada_direccion": "Dirección Llegada",
            "gre_transportista_placa_numero": "Placa Vehículo",
        }

        non_completed_fields = []
        for field, label in fields_strings.items():
            if not rec[field]:
                non_completed_fields.append(label)
            
        if non_completed_fields:
            error_message = "Campo(s) no completado(s) para la GRE: \n"
            for field_to_complete in non_completed_fields:
                error_message += f"-> {field_to_complete}\n"
            raise ValidationError(error_message)

        ## Validaciones formato
        if len(rec.gre_serie) != 4:
            raise ValidationError("La serie debe contener 4 caracteres exactos.")

        if rec.gre_tipo_de_comprobante == '7' and not rec.gre_serie.startswith('T'):
            raise ValidationError("Para GRE Remitente, la serie debe empezar con 'T'.")
        if rec.gre_tipo_de_comprobante == '8' and not rec.gre_serie.startswith('V'):
            raise ValidationError("Para GRE Transportista, la serie debe empezar con 'V'.")

        if len(str(rec.gre_numero)) > 8:
            raise ValidationError("El número debe tener como máximo 8 dígitos.")

        if rec.gre_peso_bruto_total <= 0:
            raise ValidationError("El peso bruto total debe ser mayor a 0.")

        ## Check documento anexo
        if not (rec.gre_account_move_id) and not (rec.gre_documento_numero and rec.gre_documento_serie):
            raise ValidationError("Falta ingresar el documento asociado a la guía.")
        
        if rec.gre_account_move_id:
            for account_move in rec.gre_account_move_id:
                if account_move.sequence_number == 0:
                    raise ValidationError("La serie y el número deben existir para todas las facturas")

        if rec.gre_documento_serie and len(rec.gre_documento_serie) != 4:
            raise ValidationError("La serie del documento asociadodebe contener 4 caracteres exactos.")

        if rec.gre_documento_numero and (rec.gre_documento_numero < 0 or rec.gre_documento_numero > 99999999):
            raise ValidationError("El número correlativo del documento asociado debe tener máximo 8 dígitos.")

        ## Check items
        if not rec.move_ids_without_package:
            raise ValidationError("Debe agregar ítems para generar la GRE.")
        
        for move in rec.move_ids_without_package:
            if not move.description_picking:
                raise ValidationError("Todos los ítems deben tener descripciones.")

        ## Validaciones ubigeo
        if len(rec.gre_punto_de_llegada_ubigeo) != 6:
            raise ValidationError("El ubigeo (punto de llegada) debe contener 6 caracteres.")
        
        if not self.env['pe.district'].search_count([('code', '=', rec.gre_punto_de_llegada_ubigeo)]):
            raise ValidationError(f"El ubigeo (llegada) {rec.gre_punto_de_llegada_ubigeo} no existe.")
        
        if len(rec.gre_punto_de_partida_ubigeo) != 6:
            raise ValidationError("El ubigeo (punto de partida) debe contener 6 caracteres.")
        
        if not self.env['pe.district'].search_count([('code', '=', rec.gre_punto_de_partida_ubigeo)]):
            raise ValidationError(f"El ubigeo (partida) {rec.gre_punto_de_partida_ubigeo} no existe.")

        ## Validación placa
        if "-" in rec.gre_transportista_placa_numero or (len(rec.gre_transportista_placa_numero) > 8 or len(rec.gre_transportista_placa_numero) < 6):
            raise ValidationError("El número de placa no debe contener guión (-) y debe tener de 6 a 8 caracteres.")

    def _validate_remitente_fields(self, rec):
        """Validaciones específicas para GRE Remitente"""
        required_fields = {
            "gre_motivo_de_traslado": "Motivo de Traslado",
            "gre_numero_de_bultos": "Número de Bultos",
            "gre_tipo_de_transporte": "Tipo de Transporte",
            "gre_mtc": "Registro del MTC",
        }

        non_completed = []
        for field, label in required_fields.items():
            if not rec[field]:
                non_completed.append(label)
        
        if non_completed:
            error_message = "Campos obligatorios para GRE Remitente no completados:\n"
            for field in non_completed:
                error_message += f"-> {field}\n"
            raise ValidationError(error_message)

        ## Validación motivo 13 - OTROS
        if rec.gre_motivo_de_traslado == '13' and not rec.gre_motivo_de_traslado_otros_descripcion:
            raise ValidationError("Para motivo 'OTROS' debe proporcionar la descripción.")

        ## Validación motivos 04, 18 - Código establecimiento
        if rec.gre_motivo_de_traslado in ['04', '18']:
            if not rec.gre_punto_de_partida_codigo_establecimiento_sunat or not rec.gre_punto_de_llegada_codigo_establecimiento_sunat:
                raise ValidationError("Para traslado entre establecimientos, el código de establecimiento SUNAT es obligatorio.")
            else:
                if len(rec.gre_punto_de_partida_codigo_establecimiento_sunat) != 4 or len(rec.gre_punto_de_llegada_codigo_establecimiento_sunat) != 4:
                    raise ValidationError("El código de establecimiento SUNAT debe tener 4 caracteres.")

        ## Validación transporte público
        if rec.gre_tipo_de_transporte == '01':
            if not rec.gre_transportista_documento_tipo or not rec.gre_transportista_documento_numero or not rec.gre_transportista_denominacion:
                raise ValidationError("Para transporte público, los datos del transportista son obligatorios.")
            else:
                if len(rec.gre_transportista_documento_numero) != 11:
                    raise ValidationError("El número de documento del transportista debe tener 11 caracteres.")
            

        ## Validación transporte privado - Conductor obligatorio
        if rec.gre_tipo_de_transporte == '02':
            conductor_fields = {
                "gre_conductor_documento_tipo": "Tipo Documento Conductor",
                "gre_conductor_documento_numero": "Número Documento Conductor",
                "gre_conductor_denominacion": "Denominación Conductor",
                "gre_conductor_nombre": "Nombre Conductor",
                "gre_conductor_apellidos": "Apellidos Conductor",
                "gre_conductor_numero_licencia": "Número Licencia Conductor",
            }
            
            missing_conductor = []
            for field, label in conductor_fields.items():
                if not rec[field]:
                    missing_conductor.append(label)
            
            if missing_conductor:
                error_message = "Para transporte privado, los datos del conductor son obligatorios:\n"
                for field in missing_conductor:
                    error_message += f"-> {field}\n"
                raise ValidationError(error_message)

            if len(rec.gre_conductor_numero_licencia) < 9 or len(rec.gre_conductor_numero_licencia) > 10:
                raise ValidationError("El número de licencia debe tener de 9 a 10 caracteres.")

        ## Validación número de bultos
        if rec.gre_numero_de_bultos <= 0 or rec.gre_numero_de_bultos > 999999:
            raise ValidationError("El número de bultos debe ser mayor a 0 y menor a 999999.")

        ## Validación mtc
        if rec.gre_mtc and not (rec.gre_mtc.isalnum() and rec.gre_mtc.isupper()):
            raise ValidationError("El Registro del MTC debe estar en mayúsculas sin guiones.")

    def _validate_transportista_fields(self, rec):
        """Validaciones específicas para GRE Transportista"""
        required_fields = {
            "gre_conductor_documento_tipo": "Tipo Documento Conductor",
            "gre_conductor_documento_numero": "Número Documento Conductor",
            "gre_conductor_denominacion": "Denominación Conductor",
            "gre_conductor_nombre": "Nombre Conductor",
            "gre_conductor_apellidos": "Apellidos Conductor",
            "gre_conductor_numero_licencia": "Número Licencia Conductor",
            "gre_destinatario_documento_tipo": "Tipo Documento Destinatario",
            "gre_destinatario_documento_numero": "Número Documento Destinatario",
            "gre_destinatario_denominacion": "Denominación Destinatario",
            "gre_mtc": "Registro del MTC",
            "gre_tuc_vehiculo_principal": "TUC Vehículo Principal",
        }

        non_completed = []
        for field, label in required_fields.items():
            if not rec[field]:
                non_completed.append(label)
        
        if non_completed:
            error_message = "Campos obligatorios para GRE Transportista no completados:\n"
            for field in non_completed:
                error_message += f"-> {field}\n"
            raise ValidationError(error_message)

        if len(rec.gre_conductor_numero_licencia) < 9 or len(rec.gre_conductor_numero_licencia) > 10:
            raise ValidationError("El número de licencia debe tener de 9 a 10 caracteres.")

        if rec.gre_mtc and not (rec.gre_mtc.isalnum() and rec.gre_mtc.isupper()):
            raise ValidationError("El Registro del MTC debe estar en mayúsculas sin guiones.")

        if rec.gre_tuc_vehiculo_principal:
            if len(rec.gre_tuc_vehiculo_principal) < 10 or len(rec.gre_tuc_vehiculo_principal) > 15:
                raise ValidationError("El Certificado de Habilitación Vehicular debe tener de 10 a 15 caracteres.")
            if not (rec.gre_tuc_vehiculo_principal.isalnum() and rec.gre_tuc_vehiculo_principal.isupper()):
                raise ValidationError("El Certificado debe estar en mayúsculas sin guiones.")

    def _build_payload(self, rec):
        """Construir payload según tipo de GRE"""
        items = [
            {
                "unidad_de_medida": "NIU",
                "codigo": move.product_id.product_tmpl_id.default_code,
                "descripcion": move.description_picking,
                "cantidad": str(move.quantity)
            }
            for move in rec.move_ids_without_package
        ]

        documentos_relacionados = []
        if rec.gre_tipo_documento == "01":
            documentos_relacionados.extend([
                {
                    "tipo": rec.gre_tipo_documento,
                    "serie": account_move.l10n_latam_document_type_id.doc_code_prefix + "001",
                    "numero": account_move.sequence_number
                } 
                for account_move in rec.gre_account_move_id
            ])
        else:
            documentos_relacionados.append({
                "tipo": rec.gre_tipo_documento,
                "serie": rec.gre_documento_serie,
                "numero": str(rec.gre_documento_numero)
            })

        ## Payload base común
        payload = {
            "operacion": rec.gre_operacion,
            "tipo_de_comprobante": int(rec.gre_tipo_de_comprobante),
            "serie": rec.gre_serie,
            "numero": str(rec.gre_numero),
            "cliente_tipo_de_documento": int(rec.gre_cliente_tipo_de_documento),
            "cliente_numero_de_documento": rec.gre_cliente_numero_de_documento,
            "cliente_denominacion": rec.gre_cliente_denominacion,
            "cliente_direccion": rec.gre_cliente_direccion,
            "fecha_de_emision": rec.gre_fecha_de_emision.strftime("%d-%m-%Y"),
            "peso_bruto_total": str(rec.gre_peso_bruto_total),
            "peso_bruto_unidad_de_medida": rec.gre_peso_bruto_unidad_de_medida,
            "fecha_de_inicio_de_traslado": rec.gre_fecha_de_inicio_de_traslado.strftime("%d-%m-%Y"),
            "transportista_placa_numero": rec.gre_transportista_placa_numero.upper(),
            "punto_de_partida_ubigeo": rec.gre_punto_de_partida_ubigeo,
            "punto_de_partida_direccion": rec.gre_punto_de_partida_direccion,
            "punto_de_llegada_ubigeo": rec.gre_punto_de_llegada_ubigeo,
            "punto_de_llegada_direccion": rec.gre_punto_de_llegada_direccion,
            "enviar_automaticamente_al_cliente": str(rec.gre_enviar_automaticamente_al_cliente).lower(),
            "items": items,
            "documento_relacionado": documentos_relacionados,
        }

        ## Campos específicos para GRE Remitente
        if rec.gre_tipo_de_comprobante == '7':
            payload.update({
                "motivo_de_traslado": rec.gre_motivo_de_traslado,
                "numero_de_bultos": str(int(rec.gre_numero_de_bultos)),
                "tipo_de_transporte": rec.gre_tipo_de_transporte,
            })

            if rec.gre_motivo_de_traslado == '13' and rec.gre_motivo_de_traslado_otros_descripcion:
                payload["motivo_de_traslado_otros_descripcion"] = rec.gre_motivo_de_traslado_otros_descripcion

            if rec.gre_motivo_de_traslado in ['04', '18']:
                payload["punto_de_partida_codigo_establecimiento_sunat"] = rec.gre_punto_de_partida_codigo_establecimiento_sunat
                payload["punto_de_llegada_codigo_establecimiento_sunat"] = rec.gre_punto_de_llegada_codigo_establecimiento_sunat

            if rec.gre_tipo_de_transporte == '01':
                payload.update({
                    "transportista_documento_tipo": rec.gre_transportista_documento_tipo,
                    "transportista_documento_numero": rec.gre_transportista_documento_numero,
                    "transportista_denominacion": rec.gre_transportista_denominacion,
                })

            if rec.gre_tipo_de_transporte == '02':
                payload.update({
                    "conductor_documento_tipo": rec.gre_conductor_documento_tipo,
                    "conductor_documento_numero": rec.gre_conductor_documento_numero,
                    "conductor_denominacion": rec.gre_conductor_denominacion,
                    "conductor_nombre": rec.gre_conductor_nombre.upper(),
                    "conductor_apellidos": rec.gre_conductor_apellidos.upper(),
                    "conductor_numero_licencia": rec.gre_conductor_numero_licencia,
                })

        ## Campos específicos para GRE Transportista
        elif rec.gre_tipo_de_comprobante == '8':
            payload.update({
                "conductor_documento_tipo": rec.gre_conductor_documento_tipo,
                "conductor_documento_numero": rec.gre_conductor_documento_numero,
                "conductor_denominacion": rec.gre_conductor_denominacion,
                "conductor_nombre": rec.gre_conductor_nombre.upper(),
                "conductor_apellidos": rec.gre_conductor_apellidos.upper(),
                "conductor_numero_licencia": rec.gre_conductor_numero_licencia,
                "destinatario_documento_tipo": rec.gre_destinatario_documento_tipo,
                "destinatario_documento_numero": rec.gre_destinatario_documento_numero,
                "destinatario_denominacion": rec.gre_destinatario_denominacion,
            })

            if rec.gre_mtc:
                payload["mtc"] = rec.gre_mtc

            if rec.gre_tuc_vehiculo_principal:
                payload["tuc_vehiculo_principal"] = rec.gre_tuc_vehiculo_principal

        if rec.gre_observacion:
            payload["observaciones"] = rec.gre_observacion

        return payload


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
                    "tipo_de_comprobante": int(self.gre_tipo_de_comprobante),
                    "serie": self.gre_serie,
                    "numero": self.gre_numero
                }),
                timeout=10
            )
            response.raise_for_status()

            self.gre_enlace = response.json().get('enlace', False)
            self.gre_pdf_zip_base64 = response.json().get('pdf_zip_base64', False)
            
        except Exception as e:
            _logger.info(f"\nCONSULTA GRE ERROR: {response.text if response else ''}\nError: {str(e)}")
            raise UserError(f"\nError: {response.text if response else ''}\nError: {str(e)}")

    def write(self, vals):
        if 'gre_doc_name' in vals and isinstance(vals['gre_doc_name'], str):
            vals['gre_doc_name'] = vals['gre_doc_name'].strip()
        return super().write(vals)

    def name_get(self):
        res = []
        for p in self:
            gname = (p.gre_doc_name or '').strip()
            name = gname or p.name or _("(Sin nombre)")
            res.append((p.id, name))
        return res