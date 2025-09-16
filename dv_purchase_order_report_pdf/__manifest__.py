{
	'name': "Orden de compra - Compras",
	'summary': "Añade nuevas funcionalidades al módulo de compras, y añade un nuevo reporte PDF",
	'author': 'Develogers',
	'maintainer': 'Dany Chavez',
	'website': 'https://develogers.com',
	'support': 'especialistas@develogers.com',
	'live_test_url': 'https://demo.develogers.com',
	'license': 'LGPL-3',
	'category': 'Extra Tools',
	'version': '17.0.1.0.0',
	'depends': [
  		'purchase_stock',
		'stock',
		'hr'
	],
	'data': [
		'views/purchase_order_view.xml',
		'reports/purchase_order_custom_report.xml',
		#'templates/external_layout_standard.xml'
	],
	'images': [],
	'installable': True,
	'application': False,
	'auto_install': False,
	'secuence': '1'
}
