from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests

class NubefactConfig(models.TransientModel):
    _inherit = 'res.config.settings'  # Hereda del modelo de configuración de Odoo
    
    # Añade un prefijo para evitar conflictos con otros módulos
    nubefact_ruta = fields.Char(string='Ruta de la API de Nubefact', config_parameter='nubefact.ruta')
    nubefact_token = fields.Char(string='Token de la API de Nubefact', config_parameter='nubefact.token')

    def test_connection(self):
        """
        Método para probar la conexión con la API de Nubefact.
        """
        self.ensure_one()
        
        # Obtiene la ruta y el token de la configuración
        ruta = self.nubefact_ruta
        token = self.nubefact_token
        
        if not ruta or not token:
            raise UserError(_("Por favor, configure la Ruta y el Token de la API de Nubefact."))
        
        # Simula una petición a la API de Nubefact (reemplazar con una llamada real si es necesario)
        try:
            response = requests.post(ruta, headers={'Authorization': f'Token token={token}', 'Content-Type': 'application/json'})
            if response.status_code not in (200, 201):
                raise UserError(f"Error de Nubefact: {response.text}")
            return True
        
        except Exception as e:
            raise UserError(_(f"Error al conectar con Nubefact: {e}"))