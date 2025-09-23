from odoo import models, fields

class Department(models.Model):
    _name = 'pe.department'
    _description = "Departamento"

    code = fields.Char(string='Código', required=True)
    name = fields.Char(string="Nombre", required=True)

    province_ids = fields.One2many('pe.province', 'department_id', string="Provincias")


class Province(models.Model):
    _name = 'pe.province'
    _description = "Provincia"

    code = fields.Char(string='Código', required=True)
    name = fields.Char(string="Nombre", required=True)

    department_id = fields.Many2one('pe.department', string="Departamento", required=True)
    district_ids = fields.One2many('pe.district', 'province_id', string="Distritos")

class District(models.Model):
    _name = 'pe.district'
    _description = "District / Ubigeo"

    code = fields.Char(string='Código Ubigeo', required=True)
    name = fields.Char(string="Nombre", required=True)
    
    province_id = fields.Many2one('pe.province', string="Provincia")
    department_id = fields.Many2one(related='province_id.department_id', store=True)

