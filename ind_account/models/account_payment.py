from odoo import fields,models


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    conciliation_id = fields.Char(string='Relacion transferencia', copy=False)

    def action_post(self):
        super(AccountPayment, self).action_post()

        for payment in self:
            if payment.is_internal_transfer:

                #Ubicamos la cuenta puente configurada en res.config.settings
                cta_puente = payment.journal_id.company_id.transfer_account_id.id

                asiento_generado=payment.move_id.id

                id_conciliacion = self.env['account.move.line'].search([('move_id','=',asiento_generado),('account_id','=',cta_puente)]).full_reconcile_id.id

                lista_aml=self.env['account.move.line'].search([('full_reconcile_id.id','=',id_conciliacion)]).ids
                lista_am=self.env['account.move'].search([('line_ids','in',lista_aml)])

                payments = self.env['account.payment'].search([('move_id', 'in', lista_am.ids)])

                for related_payment in payments:
                    related_payment.conciliation_id = str(id_conciliacion)
            else:
                asiento_generado=payment.move_id
                for line in asiento_generado.line_ids:
                    # Actualizamos el campo 'name' con el contenido de 'factura_pagar'
                    if line.account_id.account_type=='liability_payable':
                        line.name = payment.factura_pagar or line.name
                        line.tipo_documento = payment.tipo_documento