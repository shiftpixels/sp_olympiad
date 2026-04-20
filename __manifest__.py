{
    'name': "Olympiad Core",
    'version': '1.0.0',
    'category': 'Administration',
    'summary': 'Core module for Olympiad Management Suite',
    'description': """
Olympiad Core
=============
Core module providing the foundation for the Olympiad Management Suite.
""",
    'author': "ShiftPixels",
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'website',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/olympiad_category_views.xml',
        'views/olympiad_event_views.xml',
        'views/olympiad_category_reports.xml',
        'views/res_config_settings_views.xml',
        'views/website_templates.xml',
        'views/menu_views.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
