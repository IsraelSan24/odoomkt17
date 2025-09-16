{
    'name':'Photo Gallery',
    'summary':'Photo Gallery',
    'version':'1.0.0',
    'author':'Aaron Ilizarbe - Marketing Alterno',
    'license':'AGPL-3',
    'depends':[
        'base','product'
    ],
    'data':[
        'security/security.xml',
        'security/ir_model_access.xml',

        'data/ir_sequence_data.xml',

        'views/gallery_view.xml',
        'views/menu_views.xml',
    ],
    'installable':True,
    'application':True,
    'auto_install':False,
}