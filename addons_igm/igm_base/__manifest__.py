{
    'name': "IGM Base",
    'version': '18.0.1.0.0',
    'summary': "Shared foundation layer: common IGM models, fields and mixins reused across custom apps",
    'description': """
Low-level dependency module for the IGM custom app suite.

It holds the shared data layer that more than one IGM app relies on — common fields on
standard models (res.partner, project.task, ...), mixins and any genuinely cross-app custom
models — so that no single end-user app owns definitions the others depend on. Apps such as
igm_objektleiter_app, igm_fsm, igm_fsm_api and igm_cleaning_onboarding depend on this module.

This is technical infrastructure (no app tile). Definitions are migrated in here deliberately,
only once they are shared, during dedicated refactor sessions.
""",
    'category': 'Technical',
    'author': "IGM",
    'website': "https://interglobe.eu",
    'license': 'LGPL-3',
    'depends': [
        'base',
    ],
    'data': [
    ],
    'installable': True,
    'application': False,
}
