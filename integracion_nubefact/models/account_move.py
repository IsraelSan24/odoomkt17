from odoo import models, fields, api, _
import json
import requests
from datetime import datetime, timedelta
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Campos para almacenar el estado del envío a Nubefact
    nubefact_enviado = fields.Boolean(string='Enviado a Nubefact', default=False, copy=False)
    nubefact_respuesta = fields.Text(string='Respuesta de Nubefact', copy=False)

    def _preparar_datos_nubefact(self):
        """
        Prepara los datos de la factura en el formato requerido por Nubefact.
        """
        self.ensure_one()  # Asegura que self es un solo registro

        # Mapeo de tipos de documento
        tipo_de_comprobante_map = {
            'out_invoice': 1,  # Factura
            'out_refund': 3,  # Nota de Crédito
            'in_invoice': 1,
            'in_refund': 3,
        }

        # Mapeo de tipo de documento del cliente
        cliente_tipo_de_documento_map = {
            'ruc': 6,
            'dni': 1,
            'extranjero': 4,  # Carnet de Extranjería
            'pasaporte': 7,
            'varios': 0,
        }

        # Obtener el tipo de documento del cliente
        tipo_documento_cliente = cliente_tipo_de_documento_map.get(
            self.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code, 0)

        # Preparar los items
        items = []
        for line in self.invoice_line_ids:
            # Calcular el tipo de IGV.  Esto es un ejemplo, el cálculo real puede ser más complejo.
            if line.tax_ids:
                tipo_de_igv = 1  # Gravado
            else:
                tipo_de_igv = 1  # Ajustar esto según la lógica de tu negocio

            valor_unitario = line.price_subtotal / line.quantity if line.quantity else 0.0
            precio_unitario = line.price_total / line.quantity if line.quantity else 0.0
            subtotal = line.price_subtotal
            igv = line.price_total - line.price_subtotal
            total = line.price_total

            item = {
                "unidad_de_medida": line.product_uom_id.sunat_code or 'NIU',
                "codigo": line.product_id.default_code or '001',
                "descripcion": line.name,
                "cantidad": line.quantity,
                "valor_unitario": round(valor_unitario, 2),
                "precio_unitario": round(precio_unitario, 2),
                "descuento": "",  # Si tienes descuento, inclúyelo aquí
                "subtotal": round(subtotal, 2),
                "tipo_de_igv": tipo_de_igv,
                "igv": round(igv, 2),
                "total": round(total, 2),
                "anticipo_regularizacion": False,
                "anticipo_comprobante_serie": "",
                "anticipo_comprobante_numero": ""
            }
            items.append(item)
        
        serie_raw, numero_raw = self.name.split(' ', 1)
        serie = f"{serie_raw}001"  # Puedes parametrizar esto si hay más de una serie
        numero = numero_raw.zfill(8)

        data = {
            "operacion": "generar_comprobante",
            "tipo_de_comprobante": tipo_de_comprobante_map.get(self.move_type, 1),
            "serie": serie,  # Usar la serie del diario
            "numero": numero,  # Extraer el número de la factura
            "sunat_transaction": 1,  # Venta interna (ajustar si es necesario)
            "cliente_tipo_de_documento": 6,
            "cliente_numero_de_documento": self.partner_id.vat or '00000000',  # RUC o DNI
            "cliente_denominacion": self.partner_id.name,
            "cliente_direccion": self.partner_id.street or 'Dirección no especificada',
            "cliente_email": self.partner_id.email or '',
            "cliente_email_1": "",
            "cliente_email_2": "",
            "fecha_de_emision": self.invoice_date.strftime('%Y-%m-%d'),
            "fecha_de_vencimiento": self.invoice_date_due.strftime('%Y-%m-%d'),
            "moneda": 1 if self.currency_id.name == 'PEN' else 2,  # 1: Soles, 2: Dólares
            "tipo_de_cambio": "",  # Opcional, se debe calcular si la moneda es diferente a PEN
            "porcentaje_de_igv": 18.00,
            "descuento_global": "",
            "total_descuento": "",
            "total_anticipo": "",
            "total_gravada": self.amount_untaxed,
            "total_inafecta": "",
            "total_exonerada": "",
            "total_igv": self.amount_tax,
            "total_gratuita": "",
            "total_otros_cargos": "",
            "total": self.amount_total,
            "percepcion_tipo": "",
            "percepcion_base_imponible": "",
            "total_percepcion": "",
            "detraccion": False,
            "observaciones": "",
            "documento_que_se_modifica_tipo": "",
            "documento_que_se_modifica_serie": "",
            "documento_que_se_modifica_numero": "",
            "tipo_de_nota_de_credito": "",
            "tipo_de_nota_de_debito": "",
            "enviar_automaticamente_a_la_sunat": True,
            "enviar_automaticamente_al_cliente": False,
            "codigo_unico": "",
            "condiciones_de_pago": self.payment_reference or '',
            "medio_de_pago": "",
            "placa_vehiculo": "",
            "orden_compra_servicio": "",
            "tabla_personalizada_codigo": "",
            "formato_de_pdf": "A4",
            "items": items,
        }
        return data

    def action_enviar_nubefact(self):
        """
        Envía la factura a Nubefact.
        """
        self.ensure_one()

        # Solo permitir enviar si la factura está en estado 'posted'
        if self.state != 'posted':
            raise UserError("Solo puede enviar facturas en estado Publicado.")

        # Preparar los datos para Nubefact
        data = self._preparar_datos_nubefact()
        json_string_to_send = json.dumps(data, indent=4, ensure_ascii=False).encode('utf-8')

        # Obtener la configuración de Nubefact
        ruta = self.env['ir.config_parameter'].sudo().get_param('nubefact.ruta')
        token = self.env['ir.config_parameter'].sudo().get_param('nubefact.token')

        if not ruta or not token:
            raise UserError(
                "Por favor, configure la Ruta y el Token de la API de Nubefact en la configuración.")
        
        _logger.info("Payload a enviar a Nubefact:\n%s", json.dumps(data, indent=4, ensure_ascii=False))

        # Enviar a Nubefact
        try:
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
                'Authorization': f'Token token={token}'
            }
            response = requests.post(ruta, headers=headers, data=json_string_to_send, timeout=60)
            response.raise_for_status()  # Lanza excepción para errores HTTP
            json_response = response.text
        except requests.exceptions.RequestException as e:
            self.nubefact_respuesta = f"Error de conexión: {e}"
            self.nubefact_enviado = False
            raise UserError(f"Error al enviar a Nubefact: {e}")

        # Procesar la respuesta de Nubefact
        try:
            response_dict = json.loads(json_response)
            self.nubefact_respuesta = json.dumps(response_dict, indent=4, ensure_ascii=False)

            if "errors" in response_dict:
                self.nubefact_enviado = False
                error_message = "\n".join(response_dict['errors'])
                raise UserError(f"Errores de Nubefact: {error_message}")
            else:
                self.nubefact_enviado = True
                # Puedes guardar más información de la respuesta si es necesario
                # self.nubefact_url = response_dict.get('url')
        except json.JSONDecodeError:
            self.nubefact_respuesta = f"Respuesta inválida de Nubefact: {json_response}"
            self.nubefact_enviado = False
            raise UserError(f"Respuesta inválida de Nubefact (no es JSON): {json_response}")
        except Exception as e:
            self.nubefact_respuesta = f"Error inesperado: {e}"
            self.nubefact_enviado = False
            raise UserError(f"Error inesperado al procesar la respuesta de Nubefact: {e}")

        return True  # Indicar que la operación fue exitosa