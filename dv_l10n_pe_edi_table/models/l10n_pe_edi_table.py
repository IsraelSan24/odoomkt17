from odoo import models, fields, api
from odoo.osv import expression


class TableTmpl(models.Model):
    _name = 'l10n_pe_edi.table.tmpl'
    _description = 'Table Template'
    _sql_constraints = [
        ("code_uniq", "unique(code)", ("El codigo debe ser unico.")),
    ]
    active = fields.Boolean(string='Active', default=True)
    code = fields.Char(string='Código', size=4, index=True, required=True)
    name = fields.Char(string='Descripción', index=True, required=True)

    def name_get(self):
        result = []
        for table in self:
            result.append((table.id, "%s %s" % (table.code, table.name or '')))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', ('name', 'ilike', name), ('code', 'ilike', name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)


class Table01(models.Model):
    _name = "l10n_pe_edi.table.01"
    _description = 'Tabla 01: Tipo de medio de pago'
    _inherit = 'l10n_pe_edi.table.tmpl'

    code = fields.Char(string='Código', size=3, required=True)


class Table02(models.Model):
    _name = "l10n_pe_edi.table.02"
    _description = 'Tabla 02: Tipo de documento de identidad'
    _inherit = 'l10n_pe_edi.table.tmpl'

    code = fields.Char(string='Código', size=1, required=True)


class Table03(models.Model):
    _name = "l10n_pe_edi.table.03"
    _description = 'Tabla 03: Entidad financiera'
    _inherit = 'l10n_pe_edi.table.tmpl'

    code = fields.Char(string='Código', size=2, required=True)


class Table05(models.Model):
    _name = "l10n_pe_edi.table.05"
    _description = 'Tabla 05: Tipo de existencia'
    _inherit = 'l10n_pe_edi.table.tmpl'

    code = fields.Char(string='Código', size=2, required=True)


class Table06(models.Model):
    _name = "l10n_pe_edi.table.06"
    _description = 'Tabla 06: Código de la unidad de medida'
    _inherit = 'l10n_pe_edi.table.tmpl'

    code = fields.Char(string='Código', size=3, required=True)


class Table07(models.Model):
    _name = "l10n_pe_edi.table.07"
    _description = 'Tabla 07: Tipo de intangible'
    _inherit = 'l10n_pe_edi.table.tmpl'

    code = fields.Char(string='Código', size=3, required=True)


class Table08(models.Model):
    _name = "l10n_pe_edi.table.08"
    _description = 'Tabla 08: Código del libro o registro'
    _inherit = 'l10n_pe_edi.table.tmpl'

    code = fields.Char(string='Código', size=3, required=True)


class Table09(models.Model):
    _name = "l10n_pe_edi.table.09"
    _description = 'Tabla 09: Código de la cuenta contable'
    _inherit = 'l10n_pe_edi.table.tmpl'

    code = fields.Char(string='Código', size=5, required=True)


class Table11(models.Model):
    _name = "l10n_pe_edi.table.11"
    _description = 'Tabla 11: Código de la Aduana'
    _inherit = 'l10n_pe_edi.table.tmpl'

    code = fields.Char(string='Código', size=3, required=True)


class Table12(models.Model):
    _name = "l10n_pe_edi.table.12"
    _description = 'Tabla 12: Tipo de operación'
    _inherit = 'l10n_pe_edi.table.tmpl'

    code = fields.Char(string='Código', size=2, required=True)


class Table13(models.Model):
    _name = "l10n_pe_edi.table.13"
    _description = 'Tabla 13: Catálogo de existencias'
    _inherit = 'l10n_pe_edi.table.tmpl'

    code = fields.Char(string='Código', size=1, required=True)


class Table14(models.Model):
    _name = "l10n_pe_edi.table.14"
    _description = 'Tabla 14: Método de valuación'
    _inherit = 'l10n_pe_edi.table.tmpl'

    code = fields.Char(string='Código', size=1, required=True)


class Table15(models.Model):
    _name = "l10n_pe_edi.table.15"
    _description = 'Tabla 15: Tipo de título'
    _inherit = 'l10n_pe_edi.table.tmpl'

    code = fields.Char(string='Código', size=2, required=True)


class Table16(models.Model):
    _name = "l10n_pe_edi.table.16"
    _description = 'Tabla 16: Tipo de acciones o participaciones'
    _inherit = 'l10n_pe_edi.table.tmpl'

    code = fields.Char(string='Código', size=3, required=True)


class Table17(models.Model):
    _name = "l10n_pe_edi.table.17"
    _description = 'Tabla 17: Plan de cuentas'
    _inherit = 'l10n_pe_edi.table.tmpl'

    code = fields.Char(string='Código', size=2, required=True)


class Table18(models.Model):
    _name = "l10n_pe_edi.table.18"
    _description = 'Tabla 18: Tipo de activo fijo'
    _inherit = 'l10n_pe_edi.table.tmpl'

    code = fields.Char(string='Código', size=1, required=True)


class Table19(models.Model):
    _name = "l10n_pe_edi.table.19"
    _description = 'Tabla 19: Estado de activo fijo'
    _inherit = 'l10n_pe_edi.table.tmpl'

    code = fields.Char(string='Código', size=1, required=True)


class Table20(models.Model):
    _name = "l10n_pe_edi.table.20"
    _description = 'Tabla 20: Método de depreciación'
    _inherit = 'l10n_pe_edi.table.tmpl'

    code = fields.Char(string='Código', size=1, required=True)


class Table21(models.Model):
    _name = "l10n_pe_edi.table.21"
    _description = 'Tabla 21: Código de agrupamiento del costo de producción valorizado anual'
    _inherit = 'l10n_pe_edi.table.tmpl'

    code = fields.Char(string='Código', size=1, required=True)


class Table22(models.Model):
    _name = "l10n_pe_edi.table.22"
    _description = 'Tabla 22: Catálogo de estados financieros'
    _inherit = 'l10n_pe_edi.table.tmpl'

    code = fields.Char(string='Código', size=2, required=True)


class Table25(models.Model):
    _name = "l10n_pe_edi.table.25"
    _description = 'Tabla 25: Convenios para evitar la doble tributación'
    _inherit = 'l10n_pe_edi.table.tmpl'

    code = fields.Char(string='Código', size=2, required=True)


class Table27(models.Model):
    _name = "l10n_pe_edi.table.27"
    _description = 'Tabla 27: Tipo de vinculación económica'
    _inherit = 'l10n_pe_edi.table.tmpl'

    rent_tax_law_type = fields.Char(string='Tipo de vinculación económica',
                                    help='Tipo de vinculación económica según el Reglamento de la Ley del Impuesto a la Renta - D.S. N° 122-94-EF y modificatorias')
    code = fields.Char(string='Código', size=2, required=True)


class Table30(models.Model):
    _name = "l10n_pe_edi.table.30"
    _description = 'Tabla 30: Clasificación de los bienes y servicios adquiridos'
    _inherit = 'l10n_pe_edi.table.tmpl'

    code = fields.Char(string='Código', size=1, required=True)


class Table31(models.Model):
    _name = "l10n_pe_edi.table.31"
    _description = 'Tabla 31: Tipo de renta'
    _inherit = 'l10n_pe_edi.table.tmpl'

    code = fields.Char(string='Código', size=2, required=True)
    rent_law_article = fields.Char(
        string='Artículo de la Ley del Impuesto a la Renta y su Reglamento')
    rent_ocde_code = fields.Char(string='Código de Renta según la OCDE')


class Table32(models.Model):
    _name = "l10n_pe_edi.table.32"
    _description = 'Tabla 32: Modalidad del servicio prestado por el sujeto no domiciliado'
    _inherit = 'l10n_pe_edi.table.tmpl'

    code = fields.Char(string='Código', size=1, required=True)


class Table33(models.Model):
    _name = "l10n_pe_edi.table.33"
    _description = 'Tabla 33: Exoneraciones de operaciones de no domiciliados (ART. 19 de la ley del impuesto a la renta)'
    _inherit = 'l10n_pe_edi.table.tmpl'

    code = fields.Char(string='Código', size=1, required=True)
    
class Table34(models.Model):
    _name = "l10n_pe_edi.table.34"
    _description = 'Tabla 34: Código de los rubros de los estados financieros'
    _inherit = 'l10n_pe_edi.table.tmpl'

    parent_id = fields.Many2one('l10n_pe_edi.table.34', 'Padre', index=True, ondelete='cascade')
    child_ids = fields.One2many('l10n_pe_edi.table.34', 'parent_id', 'Hijos')
    
    code = fields.Char(string='Código', size=6, required=False)
    sequence = fields.Integer(
        required=True,
        default=1,
        string='Secuencia'
    )
    eeff_type = fields.Selection(
        selection=[
            ('3.1', '3.1 ESF'),
            ('3.18', '3.18 EFEMD'),
            ('3.19', '3.19 ECPN'),
            ('3.20', '3.20 EERR'),
            ('3.24', '3.24 ERI'),
            ('3.25', '3.25 EFEMI')
        ],
        string='Tipo'
    )
    
class Table35(models.Model):
    _name = "l10n_pe_edi.table.35"
    _description = 'Tabla 35: Países'
    _inherit = 'l10n_pe_edi.table.tmpl'

    code = fields.Char(string='Código', size=4, required=True)