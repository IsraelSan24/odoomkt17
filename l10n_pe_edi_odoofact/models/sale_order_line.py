#######################################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
#######################################################################################

from odoo import models, api, fields


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    l10n_pe_edi_is_free_product = fields.Boolean(
        string="Free",
        compute="_compute_l10n_pe_edi_is_free_product",
        help="Is free product?",
    )

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        if self.is_downpayment:
            invoice_lines = self.invoice_lines.filtered(
                lambda x: x.parent_state == "posted"
            )
            res["l10n_pe_edi_advance_serie"] = (
                invoice_lines
                and str(invoice_lines[0].move_id.sequence_prefix)[0:4]
                or ""
            )
            res["l10n_pe_edi_advance_number"] = (
                invoice_lines and invoice_lines[0].move_id.sequence_number or 0
            )
        return res

    @api.depends("discount")
    def _compute_l10n_pe_edi_is_free_product(self):
        for line in self:
            line.l10n_pe_edi_is_free_product = True if line.discount == 100.0 else False
    
    @api.depends('product_id', 'company_id', 'l10n_pe_edi_is_free_product')
    def _compute_tax_id(self):
        res = super(SaleOrderLine, self)._compute_tax_id()
        for line in self:
            if (
                line.display_type not in ["line_section","line_note"]
                and line.l10n_pe_edi_is_free_product
            ):
                free_tax = self.env['account.tax'].search([
                    ("l10n_pe_edi_tax_code", "=", "9996"),
                    ("company_id", "=", line.company_id.id)
                ], limit=1)
                if free_tax:
                    line.tax_id = [(6, 0, [free_tax.id])]
        return res
