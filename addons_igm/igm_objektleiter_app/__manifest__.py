{
    'name': "IGM Field Service – Objektleiter Dashboard (OWL)",
    'summary': "Drag-and-drop planning board: cleaning sites, their 7-day field-service tasks, and team assignment",
    'description': """
An OWL client-action dashboard for the Objektleiter (site coordinator).

He sees every Reinigungsobjekt he is responsible for, expands each site to its field-service
tasks over the next 7 days, and dispatches his team by dragging an employee tile onto a task:
 - onto an unassigned task -> assign,
 - onto an assigned task -> choose: assign additionally / substitute once / substitute the
   whole recurring series.

Assignment writes project.task.user_ids through a thin backend on project.task, so the standard
FSM planning stays the single source of truth.
""",
    'author': "IGM",
    'website': "https://interglobe.eu",
    'category': 'Services/Field Service',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',
    'depends': [
        'igm_fsm_api',
        'igm_kpis',
        'hr',
        'web',
    ],
    'data': [
        'views/res_partner_views.xml',
        'views/objektleiter_app_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'igm_objektleiter_app/static/src/**/*',
        ],
    },
    'application': True,
    'installable': True,
}
