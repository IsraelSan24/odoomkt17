from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    api_token = fields.Char(
        string="Token API.net",
        config_parameter='indomin.api_token_integration',
        help="Token para consultas RUC, DNI y Tipo de cambio, puede conseguir un token en https://apis.net.pe/"
    )
