{
    'name':'Stock Summary',
    'summary':'Stock Summary',
    'version':'1.0.0',
    'author':'Fabrizio Mori - Marketing Alterno',
    'license':'LGPL-3',
    'depends':[
        'stock',
        'product',
        'mkt_report_formats',
        'mkt_serie_state',
        'mkt_supervision',
    ],
    'data':[
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        
        'wizard/stock_summary_report_wiz.xml',

        'views/stock_summary_out_views.xml',
        'views/stock_summary_in_views.xml',
        'views/stock_summary_views.xml',
        'views/menu_views.xml',
    ],
    'installable':True,
    'auto_install':False,
    'application':True
}