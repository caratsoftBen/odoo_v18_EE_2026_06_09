{
    'name': "IGM Cleaning Service – User Provisioning",
    'summary': "Stable API to create a cleaning-service user (partner + user + employee + Cleaner role)",
    'description': """
Exposes one public, RPC-callable method as a stable façade for provisioning a
cleaning field-service worker:

    res.users.create_user_for_cleaning_service(payload)

It creates res.partner + res.users + hr.employee wired together and grants the
'Cleaner' authorization group (igm_fsm.group_fsm_cleaner), so the user can use
the Field Service "mark as done" GUI and log timesheets — nothing more.

Callers speak a stable external vocabulary (no Odoo ids leak in or out); the
method maps it to internal records and returns a stable result dict. Idempotent
on the login (e-mail). An hr.contract is created only when contract data is
supplied (payroll / time-off scope).
""",
    'author': "IGM",
    'website': "https://interglobe.eu",
    'category': 'Human Resources',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',
    'depends': [
        'igm_fsm',
        'hr_contract',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/cleaning_onboarding_wizard_views.xml',
    ],
    'application': False,
    'installable': True,
}
