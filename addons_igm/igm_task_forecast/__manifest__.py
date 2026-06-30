{
    'name': 'IGM Recurring Task Forecast',
    'version': '18.0.1.0.0',
    'category': 'Services/Project',
    'summary': 'Generate recurring tasks ahead over a horizon, skipping public holidays',
    'description': """
Scheduled action that populates recurring project / field-service tasks for the
coming horizon (default one month) instead of only one occurrence at a time.

- Only recurrences that are open (Forever, or Until a future end date) are extended.
- Occurrences that fall on public holidays are skipped by default.
- Horizon length, holiday skipping and the holiday calendar are configurable in
  Settings. The run frequency is configured in the standard Scheduled Actions UI.
    """,
    'author': 'caratsoft',
    'depends': ['project', 'resource', 'base_setup'],
    'data': [
        'data/ir_cron.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
