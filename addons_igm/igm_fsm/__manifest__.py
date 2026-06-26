{
    'name': "IGM Field Service – Cleaner UX",
    'summary': "Stripped-down Field Service task screen for cleaning staff",
    'description': """
Role-scoped Field Service experience for cleaning employees.

A 'Cleaner' security group lands the worker on the standard FSM task form with
the back-office clutter removed:
  * Sales Order / Products / Invoices / Create Invoice / Quotations disappear
    automatically (they are already gated to the sales/invoicing groups, which a
    cleaner is not in).
  * Sign Report / Send Report and the Customer Preview stat button are hidden for
    the Cleaner group.
Back-office users are completely unaffected.

Also ships a 'Reinigung' worksheet template as a starting point; add its fields in
Field Service → Configuration → Worksheet Templates.
""",
    'author': "IGM",
    'website': "https://interglobe.eu",
    'category': 'Services/Field Service',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',
    'depends': [
        'industry_fsm_report',
        'industry_fsm_sale',
        'timesheet_grid',
    ],
    'data': [
        'security/security_rules.xml',
        'security/ir.model.access.csv',
        'views/fsm_photo_wizard_views.xml',
        'views/project_task_views.xml',
        'data/worksheet_template.xml',
    ],
    'application': False,
    'installable': True,
}
