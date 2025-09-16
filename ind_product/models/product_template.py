from odoo import models, api, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_admin = fields.Boolean(
        compute='_compute_is_admin',
        store=False
    )

    @api.depends('default_code')
    def _compute_barcode(self):
        for record in self:
            record.barcode = record.default_code

    @api.onchange('default_code')
    def _onchange_default_code(self):
        if self.default_code:
            self.barcode = self.default_code

    @api.depends("is_admin")
    def _compute_is_admin(self):
        """Verifica si el usuario actual es administrador"""
        for record in self:
            record.is_admin = self.env.user.has_group('base.group_system')
