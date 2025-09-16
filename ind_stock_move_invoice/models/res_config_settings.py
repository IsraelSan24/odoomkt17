from odoo import models, fields, api


class Settings(models.TransientModel):
    _inherit = 'res.config.settings'

    customer_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Customer Journal',
        config_parameter='stock_move_invoice.customer_journal_id',
        help='To add customer journal',
        compute='_compute_journals',
        inverse='_set_customer_journal',
        store=False
    )
    vendor_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Vendor Journal',
        config_parameter='stock_move_invoice.vendor_journal_id',
        help='To add vendor journal',
        compute='_compute_journals',
        inverse='_set_vendor_journal',
        store=False
    )

    @api.onchange('company_id')
    def _compute_journals(self):
        for record in self:
            record.customer_journal_id = self.env['account.journal'].search([
                ('type', '=', 'sale'),
                ('company_id', '=', record.company_id.id)
            ], limit=1)

            record.vendor_journal_id = self.env['account.journal'].search([
                ('type', '=', 'purchase'),
                ('company_id', '=', record.company_id.id)
            ], limit=1)

    def _set_customer_journal(self):
        for record in self:
            self.env['ir.config_parameter'].sudo().set_param(
                'stock_move_invoice.customer_journal_id',
                record.customer_journal_id.id if record.customer_journal_id else ''
            )

    def _set_vendor_journal(self):
        for record in self:
            self.env['ir.config_parameter'].sudo().set_param(
                'stock_move_invoice.vendor_journal_id',
                record.vendor_journal_id.id if record.vendor_journal_id else ''
            )
