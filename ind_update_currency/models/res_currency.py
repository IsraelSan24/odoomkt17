import logging
import requests
from requests.adapters import HTTPAdapter
from requests.sessions import Session
from datetime import date
from odoo import models, api
from urllib3 import Retry
from odoo.exceptions import UserError
from requests.exceptions import ConnectionError, HTTPError, Timeout, TooManyRedirects, RequestException
from .exchange_rate_dto import ExchangeRateDTO


_logger = logging.getLogger(__name__)
URL_TC_SUNAT = 'https://api.apis.net.pe/v2/sunat/tipo-cambio'


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    @api.model
    def action_currency_update(self, date: date | None = None) -> None:
        token = self._get_api_token()
        value = self._check_exchange_rate(token, date)

        if not value:
            return

        sale = value.sale_price
        today = value.date           

        if sale <= 0:
            _logger.info('El precio de venta es 0 o negativo, no se actualizará el tipo de cambio')
            return

        companies = self.env['res.company'].search([
            ('currency_id.name', '=', 'PEN')
        ])

        if not companies:
            _logger.info('No se encontraron compañías con moneda PEN')
            return

        usd_currency = self.env['res.currency'].search([
            ('name', '=', 'USD')
        ])

        if not usd_currency:
            _logger.info('No se encontró la moneda USD')
            return

        for company in companies:
            active_currency = self.env['res.currency'].search([
                ('active', '=', True),
                '|',
                ('name', '=', 'PEN'),
                ('name', '=', 'USD')
            ])

            if len(active_currency) != 2:
                _logger.info('No se encontraron las monedas activas USD y PEN')
                continue

            currency_rate = self.env['res.currency.rate']

            existing_rate = currency_rate.search([
                ('currency_id', '=', usd_currency.id),
                ('name', '=', today),
                ('company_id', '=', company.id)
            ], limit=1)

            rate_value = (1 / sale) or currency_rate._get_latest_rate(usd_currency, today) or 1.0

            try:
                if existing_rate:
                    existing_rate.write({
                        'rate': rate_value
                    })
                else:
                    currency_rate.create({
                        'currency_id': usd_currency.id,
                        'rate': rate_value,
                        'name': today,
                        'company_id': company.id
                    })
                _logger.info(f'Tasa de cambio actualizada para USD en {company.name}: {sale}')
            except Exception as e:
                _logger.error(f'Error al actualizar el tipo de cambio: {e}')

    def _get_api_token(self) -> str:
        rcs = self.env['res.config.settings'].sudo().search([], limit=1)
        icp = self.env['ir.config_parameter'].sudo()

        valid_token = rcs.api_token or icp.get_param('indomin.api_token_integration')

        if not valid_token:
            _logger.info('No se ha encontrado un token válido en la coniguración del sistema')
            raise UserError('No se han configurado tokens de API válidos. Por favor, configure al menos un token de API en la configuración del sistema')
        
        return valid_token

    def _clean_data_api(self, data: dict) -> ExchangeRateDTO:
        return ExchangeRateDTO(
            purchase_price=data['precioCompra'],
            sale_price=data['precioVenta'],
            currency=data['moneda'],
            date=data['fecha']
        )

    def _check_exchange_rate(self, token: str, date_query: date | None = None) -> ExchangeRateDTO:
        session = self._create_session()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        
        final_url = f"{URL_TC_SUNAT}?date={date_query.strftime('%Y-%m-%d')}" if date_query else URL_TC_SUNAT

        try: 
            response = session.get(url=final_url, headers=headers)
            response.raise_for_status() 
            data = response.json()

            return self._clean_data_api(data)

        except ConnectionError as e:
            _logger.error(f'Error de conexión: {e}')
        except HTTPError as e:
            _logger.error(f'Error HTTP: {e}')
        except Timeout as e:
            _logger.error(f'Error de tiempo de espera: {e}')
        except TooManyRedirects as e:
            _logger.error(f'Demasiadas redirecciones: {e}')
        except ValueError as e: 
            _logger.error(f'Error de valor (posiblemente durante la decodificación JSON): {e}')
        except KeyError as e:
            _logger.error(f'Key error: {e}')
        except RequestException as e:
            _logger.error(f'Error en la solicitud: {e}')
        except Exception as e:
            _logger.error(f'Ocurrió un error inesperado: {e}')
        return None

    def _create_session(self, retries: int = 3, backoff_factor: float = 0.3) -> Session:
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

    def action_open_day_update_wizard(self):
        return {
            'name': '¿Qué día deseas actualizar?',
            'type': 'ir.actions.act_window',
            'res_model': 'res.currency.day.update',
            'view_mode': 'form',
            'view_id': self.env.ref('ind_update_currency.res_currency_day_update_view_form').id,
            'target': 'new',
        }
