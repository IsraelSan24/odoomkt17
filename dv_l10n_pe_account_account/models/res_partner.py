from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    l10n_pe_is_non_domiciled = fields.Boolean(string='No domiciliado', compute='_compute_l10n_pe_is_non_domiciled', store=True)
    
    @api.depends('country_id.code')
    def _compute_l10n_pe_is_non_domiciled(self):
        for record in self:
            if record.country_id.code != 'PE':
                l10n_pe_is_non_domiciled = True
            else:
                l10n_pe_is_non_domiciled = False
            record.l10n_pe_is_non_domiciled = l10n_pe_is_non_domiciled

    @api.constrains('vat')
    def constrains_vat(self):
        if self.l10n_latam_identification_type_id.l10n_pe_vat_code == '6' and len(self.vat) != 11:
            raise ValidationError(
                'El RUC debe ser de 11 digitos.')
        elif self.l10n_latam_identification_type_id.l10n_pe_vat_code == '1' and len(self.vat) != 8:
            raise ValidationError(
                'El DNI debe ser de 8 digitos.')
