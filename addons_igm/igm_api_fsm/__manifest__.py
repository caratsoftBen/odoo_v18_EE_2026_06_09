{
    'name': "IGM Field Service – PWA API",
    'summary': "Raw-JSON REST API between igm_fsm and the external Field Service PWA",
    'description': """
HTTP/JSON API layer for Field Service tasks, consumed by the standalone igm-fsm-pwa app.

Exposes the cleaner task-screen operations (list my open tasks, mark a task done with a
timesheet entry, post a photo) as a small REST contract under /igm/api/fsm. The business
logic lives as reusable methods on project.task, shared with the in-app GUI. Retries are
de-duplicated through an idempotency store.
""",
    'author': "IGM",
    'website': "https://interglobe.eu",
    'category': 'Services/Field Service',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',
    'depends': [
        'igm_fsm',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'application': False,
    'installable': True,
}
