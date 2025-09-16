import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    cr.execute(
    """
        UPDATE
            purchase_request_line
        SET
            analytic_distribution = jsonb_build_object(analytic_account_id::text, 100.0)
        WHERE
            analytic_account_id IS NOT NULL;
    """
    )
    _logger.info("ACTUALIZANDO 'PURCHASE.REQUEST'")
    _logger.info("ELIMINANDO LA COLUMNA 'analytic_account_id'...")
    cr.execute("ALTER TABLE purchase_request_line DROP COLUMN analytic_account_id;")

    _logger.info("ELIMINANDO LA TABLA 'account_analytic_tag_purchase_request_line_rel'...")
    cr.execute("DROP TABLE IF EXISTS public.account_analytic_tag_purchase_request_line_rel;")  
    
    cr.commit()
