# See LICENSE file for full copyright and licensing details.

{
    "name": "HMS_Integration",
    "version": "15.0.1.0.0",
    'depends': ['base','mail', 'portal'],
    "website": "https://scm.mitcloud.com/odoo-development-team/hms_integration",
    'author': "Thandar Aung, Myat Mon Cho, Khant Sithu Aung",
    'category': 'Hotelia',
    'description': """ Hotel Management Software Integration """,

    # data files always loaded at installation
    'data': [
        'security/ir.model.access.csv',
        'views/so_integration.xml',
        'views/connect.xml',
    ],

    # data files containing optionally loaded demonstration data
    'demo': [
        # 'demo/demo_data.xml',
    ],


    "summary": "Hotel Management Software Integration",
    "application": True,
    "qweb": ['static/src/xml/list_controller.xml'],

    'assets': {
        'web.assets_backend': [
            #'/hms_integration/static/src/js/list_controller.js',
            '/hms_integration/static/src/js/tree_view_button.js'

        ],
        "web.assets_qweb": [
            #'hms_integration/static/src/xml/list_controller.xml',
            'hms_integration/static/src/xml/tree_view_button.xml'
        ],
    },

    "license": "AGPL-3",
    "images": ["static/description/Hotel.png"],
    'installable': True,
    'auto_install': False,
}




