{
    'name': 'UHG Document Footer',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Custom legal footer (logos + company details) for UHG documents',
    'description': """
Adds a configurable legal footer to PDF documents (invoices, etc.) reproducing
the UHG layout: association logos plus managing director, registration, tax and
bank details in three columns. Per-company settings with an on/off toggle.
    """,
    'author': 'caratsoft',
    'depends': ['base_setup', 'account', 'web', 'l10n_din5008'],
    'data': [
        'views/res_config_settings_views.xml',
        'report/report_paperformat.xml',
        'report/report_footer_templates.xml',
        'data/igm_footer_data.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
