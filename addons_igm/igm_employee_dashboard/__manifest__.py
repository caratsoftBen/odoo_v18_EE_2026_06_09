# -*- coding: utf-8 -*-
{
    'name': 'UHG Employee Operational Workspace',
    'version': '18.0.1.0.0',
    'category': 'Operations',
    'summary': 'Tailored dashboard workspace for frontline employees.',
    'depends': ['base', 'project', 'industry_fsm', 'igm_task_forecast', 'igm_cleaning_onboarding'],
    'data': [
        'security/ir.model.access.csv',
        'views/igm_dashboard_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
