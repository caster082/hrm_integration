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
        'views/connect.xml',
        'views/so_integration.xml',
    ],

    # data files containing optionally loaded demonstration data
    'demo': [
        # 'demo/demo_data.xml',
    ],


    "summary": "Hotel Management Software Integration",
    "application": True,
    'qweb': [],
    "license": "AGPL-3",
    "images": ["static/description/Hotel.png"],
    'installable': True,
    'auto_install': False,
}




