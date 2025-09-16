from requests.adapters import HTTPAdapter
from urllib3 import Retry
from odoo import models, api, fields
import logging
import requests
from odoo.exceptions import UserError
from requests.exceptions import ConnectionError, HTTPError, Timeout, TooManyRedirects, RequestException

_logger = logging.getLogger(__name__)


class ChangeType(models.Model):
    _inherit = 'change.type'

    @api.model
    def run_change_type(self):
        token = self._get_api_token()
        url = 'https://api.apis.net.pe/v2/sunat/tipo-cambio'

        data = self._check_exchange_rate(token, url)

        if data:
            self._process_and_store_rates(data)

    def _get_api_token(self) -> str:
        """Obtiene el token de autenticación desde la configuración de Odoo."""
        rcs = self.env['res.config.settings'].sudo().search([], limit=1)
        icp = self.env['ir.config_parameter'].sudo()

        valid_token = rcs.api_token or icp.get_param('indomin.api_token_integration')

        if not valid_token:
            _logger.info('No se ha encontrado un token válido en la configuración del sistema')
            raise UserError('No se han configurado tokens de API válidos. Por favor, configure al menos un token de API en la configuración del sistema')
        
        return valid_token

    def _check_exchange_rate(self, token: str, url: str):
        """Consulta la API de tipo de cambio y devuelve los datos en formato JSON."""
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        session = self._create_session()

        try:
            response = session.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except (ConnectionError, HTTPError, Timeout, TooManyRedirects, RequestException) as e:
            _logger.error(f"Error en la solicitud a la API: {e}")
        except ValueError as e:
            _logger.error("Error al decodificar JSON: %s", e)
        except KeyError as e:
            _logger.error("Error de clave en la respuesta JSON: %s", e)
        except Exception as e:
            _logger.error("Ocurrió un error inesperado: %s", e)
        
        return None

    def _create_session(self, retries=3, backoff_factor=0.3):
        """Crea una sesión de requests con reintentos para manejar errores de conexión."""
        session = requests.Session()
        retry = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            read=retries,
            connect=retries,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def _process_and_store_rates(self, data):
        """Procesa los datos de la API y guarda los valores en el modelo change.type."""
        try:
            buy = float(data['precioCompra'])
            sell = float(data['precioVenta'])
            date = data['fecha']
        except KeyError as e:
            _logger.error(f"Error al procesar la respuesta de la API: {e}")
            return

        if buy <= 0 or sell <= 0:
            _logger.info("Los valores de compra o venta son inválidos, no se actualizará el tipo de cambio")
            return

        try:
            self.sudo().create({
                'date': date,
                'buy': buy,
                'sell': sell,
            })
            _logger.info(f'Tipo de cambio actualizado: Compra {buy}, Venta {sell} para la fecha {date}')
        except Exception as e:
            _logger.error(f"Error al guardar el tipo de cambio: {e}")