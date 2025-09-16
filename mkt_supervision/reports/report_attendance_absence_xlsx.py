import calendar
from datetime import datetime, timedelta

from odoo import models, _
from odoo.tools import date_utils

class ReportAttendanceAbsenceXlsx(models.AbstractModel):
    _name = 'report.attendance.absence.report_xlsx'
    _inherit = 'report.report_xlsx.abstract'  # para XLSX

    def generate_xlsx_report(self, workbook, data, records):
        # `records` es el recordset del wizard: podría ser varios, pero generalmente uno
        for wiz in records:
            self._get_datas_report_xlsx(workbook, wiz)

    def _get_datas_report_xlsx(self, workbook, wiz):
        """
        Genera la hoja de cálculo con:
        - Columnas: DNI, Nombre, Día1–DíaN, Totales verticales.
        - Las primeras 3 filas: 
            * Fila 1 (0-based): Mes Año (centrado sobre las columnas de días).
            * Fila 2: Día de la semana (S, D, L, M, X, J, V).
            * Fila 3: Día numérico (1, 2, 3, …).
        - Filas siguientes: un empleado por fila.
        - Luego, columnas fijas para totales (vertical rotated text).
        """

        # Preparativos
        mes = int(wiz.month)
        anio = int(wiz.year)
        first_day = datetime(anio, mes, 1).date()
        month_range = calendar.monthrange(anio, mes)  # (weekday, num_days)
        num_days = month_range[1]
        last_day = datetime(anio, mes, num_days).date()

        sheet_name = _('Asistencias %s-%s') % (wiz.month, wiz.year)
        ws = workbook.add_worksheet(sheet_name)
        ws.set_zoom(80)

        # --- Definición de anchos de columna:
        # Columna A (DNI), B (Nombre), luego columnas 3..(3+num_days-1) para cada día,
        # y luego 9 columnas de totales:
        ws.set_column(0, 0, 12)  # Col A: DNI
        ws.set_column(1, 1, 20)  # Col B: Nombre
        for col in range(2, 2 + num_days):
            ws.set_column(col, col, 3)  # cada día muy angosto (3 caracteres)
        # Finalmente, 9 columnas de totales (con texto rotado):
        for col in range(2 + num_days, 2 + num_days + 9):
            ws.set_column(col, col, 10)

        # --- Formatos:
        header_center = workbook.add_format({
            'font_color': '#FFFFFF', 'bg_color': '#4F81BD',
            'align': 'center', 'valign': 'vcenter', 'border': 1, 'bold': True
        })
        header_center_merged = workbook.add_format({
            'font_color': '#FFFFFF', 'bg_color': '#4F81BD',
            'align': 'center', 'valign': 'vcenter', 'border': 1, 'bold': True
        })
        header_day = workbook.add_format({
            'font_color': '#FFFFFF', 'bg_color': '#4F81BD',
            'align': 'center', 'valign': 'vcenter', 'border': 1
        })
        data_center = workbook.add_format({
            'align': 'center', 'valign': 'vcenter', 'border': 1
        })
        data_center_gray = workbook.add_format({
            'align': 'center', 'valign': 'vcenter', 'border': 1,
            'bg_color': '#D9D9D9'
        })
        # Formato para texto vertical:
        header_vertical = workbook.add_format({
            'font_color': '#FFFFFF', 'bg_color': '#4F81BD',
            'align': 'center', 'valign': 'bottom', 'border': 1,
            'rotation': 90, 'bold': True
        })

        # --- Escribir encabezados ---
        # Fila 0 (índice 0): Mes y Año centrado sobre columnas de día
        title = _('MES DE %s %s') % (calendar.month_name[mes].upper(), anio)
        if num_days > 0:
            ws.merge_range(0, 2, 0, 2 + num_days - 1, title, header_center_merged)
        # También ponemos "DNI" y "NOMBRE" en las filas 0-2:
        ws.merge_range(0, 0, 2, 0, _('DNI'), header_center)
        ws.merge_range(0, 1, 2, 1, _('NOMBRE'), header_center)

        # Fila 1 (índice 1): Día de la semana para cada columna de día
        for day in range(1, num_days + 1):
            fecha = datetime(anio, mes, day).date()
            weekday = fecha.weekday()  # 0=Lunes ... 6=Domingo
            # Mapeamos a sigla: L=0, M=1, X=2, J=3, V=4, S=5, D=6
            siglas = ['L', 'M', 'X', 'J', 'V', 'S', 'D']
            letra = siglas[weekday]
            ws.write(1, 2 + (day - 1), letra, header_day)

        # Fila 2 (índice 2): Día numérico
        for day in range(1, num_days + 1):
            ws.write(2, 2 + (day - 1), day, header_day)

        # Encabezados de totales (columnas 2+num_days ... 2+num_days+8),
        # texto vertical escrito de abajo hacia arriba
        totales = [
            _('DIAS TRABAJADOS'),
            _('DIAS VACACIONES'),
            _('DIAS SUBSIDIO MATERNIDAD'),
            _('LICENCIA PATERNIDAD'),
            _('DESCANSO MÉDICO MENOR 20 DÍAS'),
            _('DESCANSO MÉDICO MAYOR 20 DÍAS'),
            _('FERIADOS'),
            _('DIAS NO LABORADOS'),
            _('LICENCIA SIN GOCE DE HABER'),
        ]
        inicio_tot = 2 + num_days
        for idx, txt in enumerate(totales):
            ws.write(2, inicio_tot + idx, txt, header_vertical)

        # --- Pre-carga de datos desde la BD ---

        # 1) Obtenemos todos los empleados activos:
        query_emp = """
            SELECT he.id AS emp_id, rp.identification_id AS dni, rp.name AS nombre
            FROM hr_employee he
            JOIN res_users ru ON ru.id = he.user_id
            JOIN res_partner rp ON rp.id = ru.partner_id
            WHERE he.active = True
            ORDER BY rp.name
        """
        self.env.cr.execute(query_emp)
        employees = self.env.cr.dictfetchall()
        # employees: lista de dict {'emp_id': ..., 'dni': ..., 'nombre': ...}

        # 2) Asistencias: agrupamos por empleado y fecha
        query_att = """
            WITH attendance_data AS (
                SELECT
                    at.employee_id AS emp_id,
                    (at.check_in AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')::date AS fecha
                FROM hr_attendance at
                WHERE (at.check_in AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')::date BETWEEN %s AND %s
                  AND at.check_in IS NOT NULL
                GROUP BY at.employee_id, (at.check_in AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')::date
            )
            SELECT emp_id, fecha FROM attendance_data
        """
        self.env.cr.execute(query_att, (first_day, last_day))
        attends = self.env.cr.fetchall()
        # Convertimos a set de tuplas para búsqueda rápida:
        attend_set = set((r[0], r[1]) for r in attends)

        # 3) Ausencias: buscamos las licencias validadas que cubran cada día
        #    Solo consideramos hr_leave.state='validate'
        query_leave = """
            SELECT hl.employee_id AS emp_id,
                   (hl.date_from AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')::date AS inicio,
                   (hl.date_to   AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')::date AS fin,
                   hlt.sigla AS sigla
            FROM hr_leave hl
            JOIN hr_leave_type hlt ON hlt.id = hl.holiday_status_id
            WHERE hl.state = 'validate'
              AND (hl.date_from AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')::date <= %s
              AND (hl.date_to   AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')::date >= %s
        """
        # Elegimos de tal forma que si hay un rango que cruce el mes, quede registrado
        self.env.cr.execute(query_leave, (last_day, first_day))
        leaves_raw = self.env.cr.dictfetchall()
        # leaves_raw: lista de dict {emp_id, inicio, fin, sigla}

        # Construimos un diccionario:
        # leaves_map[(emp_id, fecha)] = 'SIGLA'
        leaves_map = {}
        for rec in leaves_raw:
            emp = rec['emp_id']
            ini = rec['inicio']
            fin = rec['fin']
            sig = rec['sigla'] or ''
            # Recorremos cada día del rango y si está dentro del mes, lo agregamos
            current = max(ini, first_day)
            end_range = min(fin, last_day)
            delta = (end_range - current).days
            for d in range(delta + 1):
                dia = current + timedelta(days=d)
                leaves_map[(emp, dia)] = sig

        # 4) Feriados de Colombia (solo conteo): si quieres marcar "F" en día festivo,
        #    deberías tener la lista de feriados (manual o módulo aparte). Aquí usaremos un
        #    recurso simple: tomamos del calendario de Colombia 2025 (puedes extender a 2024).
        #    Para simplicidad, asumiremos que quien use esto ya cargó los feriados en un modelo,
        #    pero para este ejemplo, marcaremos solo Sábados y Domingos como 'H' (fines de semana).
        #    Fines de semana ya se marcan con 'H'. No incorporamos festivos nacionales extra
        #    salvo que los tengas en un módulo de feriados.

        # --- Escribir filas de datos (a partir de la fila 3, índice base 0) ---
        row = 3
        for emp in employees:
            emp_id = emp['emp_id']
            dni = emp['dni'] or ''
            nombre = emp['nombre'] or ''
            # Columna 0: DNI
            ws.write(row, 0, dni, data_center)
            # Columna 1: Nombre
            ws.write(row, 1, nombre, data_center)

            # Variables auxiliares para totales
            tot_ausencias = 0
            tot_vacaciones = 0
            tot_subsidio = 0
            tot_paternidad = 0
            tot_medico_menor = 0
            tot_medico_mayor = 0
            tot_feriados = 0  # si tienes feriados específicos, suma aquí
            tot_no_laborados = 0  # adjunto
            tot_sin_goce = 0

            # Recorremos cada día del mes
            for dia in range(1, num_days + 1):
                fecha = datetime(anio, mes, dia).date()
                col = 2 + (dia - 1)

                # 1) ¿Es sábado o domingo?
                if fecha.weekday() in (5, 6):  # 5=Sábado, 6=Domingo
                    ws.write(row, col, 'H', data_center_gray)
                    tot_no_laborados += 1
                    continue

                # 2) ¿Tiene licencia ese día?
                key = (emp_id, fecha)
                if key in leaves_map:
                    sigla = leaves_map[key]
                    ws.write(row, col, sigla, data_center)
                    # Contabilizamos según la sigla (mapeo arbitrario):
                    # Puedes ajustar esta lógica si quieres categorizarlos de otra manera:
                    if sigla.upper() == 'V':  # Ej: Vacaciones
                        tot_vacaciones += 1
                    elif sigla.upper() == 'S':  # Ej: Subsidio maternidad
                        tot_subsidio += 1
                    elif sigla.upper() == 'P':  # Ej: Paternidad
                        tot_paternidad += 1
                    elif sigla.upper() == 'M':  # Ej: Médico menor 20
                        tot_medico_menor += 1
                    elif sigla.upper() == 'N':  # Ej: Médico mayor 20
                        tot_medico_mayor += 1
                    elif sigla.upper() == 'F':  # Ej: Feriado
                        tot_feriados += 1
                    elif sigla.upper() == 'L':  # Ej: Sin goce (licencia)
                        tot_sin_goce += 1
                    else:
                        tot_ausencias += 1  # cualquier otra ausencia
                    continue

                # 3) Si no es fin de semana ni hay licencia, revisamos asistencia
                if (emp_id, fecha) in attend_set:
                    ws.write(row, col, 'A', data_center)
                else:
                    # Si no hay asistencia ni licencia, se cuenta como día no laborado
                    ws.write(row, col, '', data_center)
                    tot_no_laborados += 1

            # 4) Rellenamos totales en las 9 columnas finales
            dias_trabajados = num_days - tot_ausencias - tot_vacaciones - tot_subsidio \
                              - tot_paternidad - tot_medico_menor - tot_medico_mayor \
                              - tot_feriados - tot_no_laborados - tot_sin_goce
            # Fila `row`, columna `2 + num_days + idx`
            tot_values = [
                dias_trabajados,
                tot_vacaciones,
                tot_subsidio,
                tot_paternidad,
                tot_medico_menor,
                tot_medico_mayor,
                tot_feriados,
                tot_no_laborados,
                tot_sin_goce,
            ]
            for idx, val in enumerate(tot_values):
                ws.write(row, inicio_tot + idx, val, data_center)

            row += 1