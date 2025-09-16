import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"
    
    leather_shoe_size = fields.Integer(
        string="Talla de zapato de cuero", 
        related="employee_id.leather_shoe_size"
    )
    rubber_boot_size = fields.Integer(
        string="Talla Bota de Jebe",
        related="employee_id.rubber_boot_size"
    )
    romper_size = fields.Char(
        string="Talla Mameluco",
        related="employee_id.romper_size"
    )
    pants_size = fields.Integer(
        string="Talla Pantalón",
        related="employee_id.pants_size"
    )   
    shirt_size = fields.Char(
        string="Talla Camisa",
        related="employee_id.shirt_size"
    )
    tshirt_size = fields.Char(
        string="Talla Polo",
        related="employee_id.tshirt_size"
    )  
    measuring_lenses = fields.Boolean(
        string="Usa lentes de medida",
        related="employee_id.measuring_lenses"
    ) 
    assets_payment = fields.Selection(
        string="Dispone de Cuenta de Haberes",
        related="employee_id.assets_payment"
    )
    bank_account_assets_true = fields.Selection(
        string="Banco Abono de Haberes True",
        related="employee_id.bank_account_assets_true"
    )
    account_number_true = fields.Char(
        string="Número de Cuenta",
        related="employee_id.account_number_true"
    )
    interbank_account_number_true = fields.Char(
        string="Número de Cuenta Interbancario",
        related="employee_id.interbank_account_number_true"
    )
    currency_type_assets_true = fields.Selection(
        string="Moneda true",
        related="employee_id.currency_type_assets_true"
    )
    bank_account_assets_false = fields.Selection(
        string="Banco Abono de Haberes False",
        related="employee_id.bank_account_assets_false"
    )
    currency_type_assets_false = fields.Selection(
        string="Moneda false", 
        related="employee_id.currency_type_assets_false"
    )
    bank_account_cts = fields.Selection(
        string="Banco CTS",
        related="employee_id.bank_account_cts"
    )
    currency_type_cts = fields.Selection(
        string="Moneda cts", 
        related="employee_id.currency_type_cts"
    )
    expiration_medical_test = fields.Date(
        string="Fecha de Vencimiento Exámen Médico",
        related="employee_id.expiration_medical_test"
    )
    expiration_isem = fields.Date(
        string="Fecha de Vencimiento ISEM", 
        related="employee_id.expiration_isem"
    )
    driver_license = fields.Char(
        string="Tipo de Licencia de conducir", 
        related="employee_id.driver_license"
    )
    expiration_license = fields.Date(
        string="Fecha de vencimiento Licencia de Conducir",
        related="employee_id.expiration_license"
    )
    license_number = fields.Char(
        string="Número de Licencia",
        related="employee_id.license_number"
    )
    expiration_license_inter = fields.Date(
        string="Fecha de Vencimiento Licencia Interna",
        related="employee_id.expiration_license_inter"
    )
    driving_course_expiration = fields.Date(
        string="Fecha de Vencimiento Curso de Manejo",
        related="employee_id.driving_course_expiration"
    )
    remaining_medical_test = fields.Integer(
        string="Tiempo de Duración(días)",
        related="employee_id.remaining_medical_test"
    )
    expiration_days_medical_test = fields.Integer(
        string="Días de caducidad del EMO trabajador", 
        related="employee_id.expiration_days_medical_test"
    )
    test_selector = fields.Selection(
        string="Selección de Prueba",
        related="employee_id.test_selector"
    )
