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
    'author': "Ahmet Cangir",
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'website',
        'auth_signup',
    ],
    'data': [
        'security/sp_olympiad_security.xml',
        'security/ir.model.access.csv',
        'views/olympiad_category_views.xml',
        'views/olympiad_event_views.xml',
        'views/olympiad_category_reports.xml',
        'views/olympiad_student_views.xml',
        'views/olympiad_project_views.xml',
        'data/remove_certificate_data.xml',
        'views/res_config_settings_views.xml',
        'views/mentor_actions.xml',
        'views/mentor_views.xml',
        'views/mentor_email_template.xml',
        'views/website_templates.xml',
        'views/menu_views.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
