from odoo import _, api, fields, models
from datetime import date, datetime
import logging

_logger = logging.getLogger(__name__)



class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    leather_shoe_size = fields.Integer(string='Talla Zapato de cuero',default=0)
    rubber_boot_size = fields.Integer(string='Talla Bota de Jebe',default=0)
    romper_size = fields.Char(string='Talla Mameluco')
    pants_size = fields.Integer(
        string='Talla Pantalón',
        default=0
    )
    shirt_size = fields.Char(string='Talla Camisa')
    tshirt_size = fields.Char(string='Talla Polo')
    measuring_lenses = fields.Boolean(string='Usa lentes de medida')

    assets_payment = fields.Selection(
        [('si', 'Sí'), ('no', 'No')],
        string='Dispone de Cuenta de Haberes',
        required=True,
        default='si',
    )
    bank_account_assets_true = fields.Selection(
        string='Banco Abono de Haberes',
        selection=[
            ('bcp', 'BCP'),
            ('bbva', 'BBVA')
        ],
    )
    account_number_true = fields.Char(
        string='Número de Cuenta',
        size=20
    )
    interbank_account_number_true = fields.Char(
        string='Número de Cuenta Interbancario',
        size=20
    )
    currency_type_assets_true = fields.Selection(
        string='Moneda',
        selection=[
            ('soles', 'Soles'),
            ('dolares', 'Dólares')
        ],
        default='soles'
    )
    bank_account_assets_false = fields.Selection(
        string='Banco Abono de Haberes',
        selection=[
            ('bcp', 'BCP'),
            ('bbva', 'BBVA')
        ],
    )
    currency_type_assets_false = fields.Selection(
        string='Moneda',
        selection=[
            ('soles', 'Soles'),
            ('dolares', 'Dólares')
        ],
        default='soles'
    )

    bank_account_cts = fields.Selection(
        string='Banco CTS',
        selection=[
            ('bcp', 'BCP'),
            ('bbva', 'BBVA')
        ]
    )
    currency_type_cts = fields.Selection(
        string='Moneda',
        selection=[
            ('soles', 'Soles'),
            ('dolares', 'Dólares')
        ],
        default='soles'
    )
    expiration_medical_test = fields.Date(
        string='Fecha de Vencimiento Exámen Médico',
        required=False,
        readonly=False,
    )
    expiration_isem = fields.Date(
        string='Fecha de Vencimiento ISEM',
        required=False,
        readonly=False
    )
    driver_license = fields.Char(
        string='Tipo de Licencia de conducir',
        size=8
    )
    expiration_license = fields.Date(
        string='Fecha de vencimiento Licencia de Conducir',
        required=False,
        readonly=False,
    )
    license_number = fields.Char(
        string='Número de Licencia',
        size=9
    )
    expiration_license_inter = fields.Date(
        string='Fecha de Vencimiento Licencia Interna',
        required=False,
        readonly=False,
    )
    driving_course_expiration = fields.Date(
        string='Fecha de Vencimiento Curso de Manejo',
        required=False,
        readonly=False,
    )
    remaining_medical_test = fields.Integer(
        string='Tiempo de Duración(días)',
        compute='_compute_remaining_days',
        store=False,
    )
    expiration_days_medical_test = fields.Integer(
        string='Días de caducidad del EMO trabajador',
        default=30
    )
    test_selector = fields.Selection(
        string='Selección de Prueba',
        selection=[
            ('si', 'Sí'),
            ('no', 'No')
        ],
        required=True,
        default='si',
    )
    
    @api.depends('expiration_medical_test')
    def _compute_remaining_days(self):
        
        # Función encargada de hallar los días restantes para el
        # vencimiento del examen médico, contados del día actual
        
        for r in self:
            if r.expiration_medical_test:
                r.remaining_medical_test = (r.expiration_medical_test - date.today()).days
            else:
                r.remaining_medical_test = 0

    # TODO: REVIEW IN ODOO17 
    @api.model
    def caducidad_emo(self):
        
        # Esta función devuelve los empleados cuyos exámenes médicos
        # están caducados y los envía en un correo a mail_to desde
        # el servidor de odoo
        
        total_dias = self.search([])
        empleados_vencidos = [] # array que se llenará con los empleados expirados  
        for r in total_dias:
            if r.expiration_medical_test:
                ale = (r.expiration_medical_test - date.today()).days   # días faltantes para expirar EMOs
                if ale <= 30:
                    empleados_vencidos.append(r.name)   # Agrega los datos de los empleados 
                else:
                    _logger.info('Examen Médico Reciente ' + r.name)
            else:
                _logger.info('No dispone de fecha de caducidad de Examen Médico')

        empleados = '<br>'.join(empleados_vencidos) # datos de empleados convertidos a texto

        if empleados != '':    
            odoobot = self.env.ref('base.user_root').id
            mail_from = 'odoobot@example.com'   # email del servidor de odoo
            mail_to = 'rrhh@indomin.net'  # r.parent_id.work_email
            userID = odoobot    # se usa usuario de odoo para tener los permisos
            mail_vals = {   # Datos del email
                'subject': 'Notificación de EMOs Vencidos',
                'author_id': userID,
                'email_from': mail_from,
                'email_to': mail_to,
                'message_type': 'email',
                'body_html': 'Estimado equipo de RRHH,' + '<br>El Examen Médico de los empleados<br><br>' # Contenido del mensaje a enviar
                + empleados
                + '<br><br>expirará antes de 30 días<br>Por favor actualizar sus datos,<br>Muchas Gracias.',
            }
            mail_id = self.env['mail.mail'].create(mail_vals)
            mail_id.send()
            _logger.info('Empleado ' + r.name + ' Correo de salida ' + mail_from)
