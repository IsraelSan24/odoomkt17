from odoo import http
from odoo.http import request
from datetime import datetime
import requests
import pytz

class SpaceBooking(http.Controller):

    @http.route('/spacebooking', type='http', auth='public', website=True)
    def space_booking(self, **kw):
        dni = kw.get('dni')
        rooms = request.env['space.room'].sudo().search([])
        items = request.env['space.booking.item'].sudo().search([])
        
        values = {'rooms': rooms, 'items': items}

        if dni:
            user_data = self.get_user_data_by_dni(dni)
            if user_data:
                values.update({
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'dni': dni,
                })
            else:
                values['error_message'] = 'No se pudo obtener los datos del DNI.'
        
        return request.render('mkt_roomreserves.reservation_form', values)

    @http.route('/reservation/submit', type='http', auth="public", website=True, methods=["POST"])
    def submit_reservation(self, **kwargs):
        reservation_datetime = kwargs.get('reservation_datetime')
        
        # Convertir a objeto datetime y ajustar a UTC-5
        local_tz = pytz.timezone('America/Bogota')  # Usa la zona horaria correcta
        naive_dt = datetime.strptime(reservation_datetime, "%Y-%m-%dT%H:%M")
        localized_dt = local_tz.localize(naive_dt)  # Añadir la zona horaria local
        start_datetime = localized_dt.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")  # Convertir a UTC

        vals = {
            'room_id': int(kwargs.get('room_id')),
            'start_datetime': start_datetime,
            'duration': float(kwargs.get('duration', 1)),
            'state': 'pending',
            'first_name': kwargs.get('first_name'),
            'last_name': kwargs.get('last_name'),
            'full_name': f"{kwargs.get('first_name', '').strip()} {kwargs.get('last_name', '').strip()}".strip(),
            'notes': kwargs.get('notes'),
            'contact': kwargs.get('contact'),
        }

        booking = request.env['space.booking'].sudo().create(vals)

        # Notificar a la recepcionista
        self.notify_receptionist(booking)

        return request.render("mkt_roomreserves.reservation_success")


    @http.route('/spacebooking/success', type='http', auth='public', website=True)
    def reservation_success(self, **kw):
        return request.render('mkt_roomreserves.reservation_success', {})

    def get_user_data_by_dni(self, dni):
        try:
            url = "https://apiperu.dev/api/dni"
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': 'Bearer 4b56a00274d444b40cc38d47e69c72d6f5a362dddbee20470b9f1dd8d6a65479'
            }
            response = requests.post(url, json={"dni": str(dni)}, headers=headers)

            if response.status_code == 200:
                data = response.json().get('data')
                if data:
                    return {
                        'first_name': data['nombres'].split(" ")[0],
                        'last_name': f"{data['apellido_paterno']} {data['apellido_materno']}"
                    }
        except Exception:
            pass
        return None


    def notify_receptionist(self, booking):
        receptionist_group = request.env.ref('mkt_roomreserves.group_receptionist')
        receptionists = request.env['res.users'].sudo().search([
            ('groups_id', 'in', [receptionist_group.id])
        ])
        
        internal_user = request.env['res.users'].sudo().browse(90)
        internal_partner_id = internal_user.partner_id.id

        if receptionists:
            notification_ids = [(0, 0, {
                'res_partner_id': receptionist.partner_id.id,
                'notification_type': 'inbox'
            }) for receptionist in receptionists]

            request.env['mail.message'].sudo().create({
                'message_type': 'notification',
                'body': (
                    f"Se ha solicitado una nueva reserva para la habitación {booking.room_id.name} "
                    f"el {booking.start_datetime}. Reservado por: {booking.first_name} {booking.last_name}."
                ),
                'subject': 'Nueva Solicitud de Reserva',
                'partner_ids': [(4, receptionist.partner_id.id) for receptionist in receptionists],
                'model': 'space.booking',
                'res_id': booking.id,
                'notification_ids': notification_ids,
                'author_id': internal_partner_id,
            })
