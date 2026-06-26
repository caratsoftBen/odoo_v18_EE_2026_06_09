{
    'name': 'IGM DE Minijob Payroll (Prototype)',
    'version': '18.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Hourly Minijob / geringfügige Beschäftigung: gross from timesheet x hourly wage',
    'description': """
Prototype German Minijob (geringfügige Beschäftigung) wage computation.

Adds the minimal Odoo payroll scaffolding to pay an hourly Minijobber:
- one Salary Structure Type ("Minijob", hourly wage),
- one Salary Structure bound to it,
- one compute rule that reads the employee's timesheet hours for the payslip
  period and multiplies them by the contract hourly wage, plus thin echo rules
  for Gross / employer flat contributions / employee deductions / Net.

The figures (flat health/pension/tax rates) are illustrative and NOT legally
certified. This is a first prototype step, not a payroll-ready localization.
    """,
    'author': 'caratsoft',
    'depends': ['hr_payroll', 'hr_timesheet'],
    'data': [
        'data/minijob_payroll_data.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
