{
    'name': "IGM Field Service – Cleaner App (OWL)",
    'summary': "In-Odoo OWL client action for the cleaner field-service screen, sharing the project.task API with the PWA",
    'description': """
The 'all in Odoo' counterpart to the standalone igm-fsm-pwa app.

A full-screen OWL client action that renders the same cleaner task screen (mark done with a
timesheet entry, adjust time, add photos, contact the Ansprechpartner) by calling the very
same reusable methods on project.task that igm_api_fsm exposes over REST — here reached
directly through the web client's ORM service (call_kw), so there is one shared backend brain
and no REST/CORS/auth layer to maintain.
""",
    'author': "IGM",
    'website': "https://interglobe.eu",
    'category': 'Services/Field Service',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',
    'depends': [
        'igm_api_fsm',
        'web',
    ],
    'data': [
        'views/fsm_app_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'igm_fsm_app/static/src/**/*',
        ],
    },
    'application': True,
    'installable': True,
}
