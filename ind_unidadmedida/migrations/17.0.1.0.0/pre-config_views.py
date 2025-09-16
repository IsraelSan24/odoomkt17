import logging
_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # modules_to_clean = [
    #     'dv_l10n_pe_sunat_ple_13',
    #     'dv_l10n_pe_sunat_ple_14',
    #     'dv_l10n_pe_sunat_ple_08',
    #     'dv_l10n_pe_sunat_ple',
    #     'dv_l10n_pe_sunat_moves_13',
    #     'dv_l10n_pe_account_account',
    #     'ind_reportelogistica',
    #     'dv_l10n_pe_sunat_catalog',
    #     'dv_l10n_pe_edi_table',
    #     'purchase_discount',
    #     'dv_account_journal_document_type',
    #     'dv_l10n_latam_document_type_manager',
    #     'dv_l10n_pe_sunat_moves_08',
    #     'dv_l10n_pe_sunat_moves_14',
    #     'purchase_analytic',
    #     'dv_stock_move_analytic_account_field',
    #     'dv_account_move_custom_currency_rate',
    #     'dv_account_move_date_currency_rate_validation',
    #     'dv_l10n_pe_sunat_reports',
    #     'dv_account_invoice_date_currency_rate',
    #     'studio_customization',
    #     'ind_hr_contract',
    #     'generic_security_restriction',
    #     'dv_l10n_pe_res_company_tax_regime_type',
    #     'dv_l10n_latam_currency_multirate'
    # ]

    # for module in modules_to_clean:
    #     try:
    #         _logger.info(f"LIMPIANDO DATOS HUÉRFANOS DEL MÓDULO: {module}...")
    #         cr.execute("""
    #             SELECT
    #                 id, res_id, model
    #             FROM
    #                 ir_model_data
    #             WHERE
    #                 model in (
    #                 'ir.ui.view',
    #                 'ir.ui.menu',
    #                 'ir.act.window'
    #                 'ir.actions.',
    #                 'ir.actions.act_url',
    #                 'ir.rule',
    #                 'ir.model',
    #                 'ir.model.fields') AND
    #                 module = %s
    #             ORDER BY
    #                 res_id desc;
    #             """, (module, ))
    #         ids_and_module_to_delete = cr.fetchall()

    #         for id, res_id, ir_module in ids_and_module_to_delete:
    #             cr.execute(f"DELETE FROM {ir_module.replace('.', '_')} WHERE id = {res_id}")
    #             cr.execute("DELETE FROM ir_model_data WHERE id = %s", (id,))
    #             _logger.info(f"-----La vista del módulo {ir_module} con el id: {res_id} se eliminó-----")
    #     except Exception as e:
    #         _logger.error(f"ALGO OCURRIO MIENTRAS SE TRATABA EL MÓDULO: {module}")
    #         _logger.error(f"ERROR: {str(e)}")
    #     cr.commit()


    module_views_to_disable = [
        'ind_service_order',
        'ind_reporte_consumos',
        'ind_sale_purchase_previous_product_cost',
        'ind_kardex_valorado_general',
        'ind_stock',
        'ind_purchase_request',
        'product_cost_invoice',
        'dv_purchase_order_report_pdf',
        'purchase_request',
        'ind_stock_move_invoice',
        'dv_stock_picking_employee_pin',
        'dv_analytic_account_target_move',
        'ind_report_stock_aging',
        'ind_campos_concar',
        'stock_no_negative',
        'garazd_product_label',
        'ind_stock_request',
        'stock_move_invoice',
        'ind_account',
        'eg_cancel_stock_move',
        'dv_account_seat_number',
        'dv_l10n_pe_account_detractions',
        'analytic_partner_history',
        'ind_product',
        'employee_personal_information',
        'product_sequence',
        'product_code_unique',
        'size_restriction_for_attachments',
    ]

    cr.execute("DELETE FROM ir_ui_view WHERE id = 2285")

    for module in module_views_to_disable:
        _logger.info(f"Revisando vistas del módulo: {module}")
        try:
            cr.execute("""
                SELECT res_id FROM ir_model_data
                WHERE model = 'ir.ui.view' AND module = %s
                ORDER BY res_id DESC;
            """, (module,))
            view_ids = [res_id for (res_id,) in cr.fetchall()]

            for res_id in view_ids:
                cr.execute("DELETE FROM ir_ui_view WHERE id = %s", (res_id,))
                _logger.info(f"Vista con ID {res_id} eliminada.")

            _logger.info(f"Todas las vistas del módulo {module} fueron eliminadas.")
        except Exception as e:
            _logger.error(f"Error al procesar el módulo {module}: {str(e)}")
        cr.commit()
