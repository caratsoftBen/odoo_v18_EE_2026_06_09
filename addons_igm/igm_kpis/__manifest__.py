{
    'name': "IGM KPIs",
    'version': '18.0.1.0.0',
    'summary': "Shared KPI provider: reusable usage metrics (hours, capacity) for the IGM app suite",
    'description': """
Low-level KPI provider for the IGM custom app suite.

Unlike igm_base (which owns shared data definitions), this module owns no persisted business
data. It exposes an abstract service model, igm.kpi, whose methods compute usage figures on
demand from standard Odoo data (contracts, timesheets, planned tasks) so that dashboards,
FSM apps and reports read one consistent set of numbers instead of each re-deriving them.

First metric: employee_remaining_hours_for_month(employee_id) — contractual monthly hour cap
minus already-logged timesheet hours minus still-outstanding planned task hours, i.e. how much
working time is left before a contractual hours limit (e.g. Minijob 40 h/month) is breached.

It also owns the visual side of KPIs: igm.kpi methods such as task_allocation() return a
renderable payload (widget, value, unit, pct, status, label) and the OWL component KpiBadge
renders it. The encoding (donut today, progress bar tomorrow) is decided here only — consuming
apps place <KpiBadge kpi="..."/> and are never touched when the design changes.

This is technical infrastructure (no app tile).
""",
    'category': 'Technical',
    'author': "IGM",
    'website': "https://interglobe.eu",
    'license': 'LGPL-3',
    'depends': [
        'hr_contract',
        'hr_timesheet',
        'project',
        'web',
    ],
    'data': [
        'views/hr_contract_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'igm_kpis/static/src/**/*',
        ],
    },
    'installable': True,
    'application': False,
}
