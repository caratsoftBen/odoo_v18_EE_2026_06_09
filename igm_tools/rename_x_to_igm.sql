-- Rename x_ -> igm_ in-place on an already-installed DB.
-- Run BEFORE restarting Odoo, then restart with:
--   -u igm_footer,igm_task_forecast,igm_employee_dashboard
-- Wrapped in a transaction: any error rolls the whole thing back.
--
--   psql -h localhost -U odoo -d odoo_v18_2026_06_11_skr03 -f igm_tools/rename_x_to_igm.sql

BEGIN;

-- ============================================================
-- 1. Module records (directory name must equal ir_module_module.name)
-- ============================================================
UPDATE ir_module_module SET name = 'igm_footer'             WHERE name = 'x_footer';
UPDATE ir_module_module SET name = 'igm_task_forecast'      WHERE name = 'x_task_forecast';
UPDATE ir_module_module SET name = 'igm_employee_dashboard' WHERE name = 'x_employee_dashboard';

-- ============================================================
-- 2. External-ID namespace (the module column on ir_model_data)
-- ============================================================
UPDATE ir_model_data SET module = 'igm_footer'             WHERE module = 'x_footer';
UPDATE ir_model_data SET module = 'igm_task_forecast'      WHERE module = 'x_task_forecast';
UPDATE ir_model_data SET module = 'igm_employee_dashboard' WHERE module = 'x_employee_dashboard';

-- ============================================================
-- 3. External-ID names that embedded the old prefix
--    (so existing records are matched in-place on -u, not duplicated/orphaned)
-- ============================================================
-- igm_footer: settings view + report templates
UPDATE ir_model_data SET name = 'res_config_settings_view_form_igm_footer' WHERE module = 'igm_footer' AND name = 'res_config_settings_view_form_x_footer';
UPDATE ir_model_data SET name = 'igm_footer_block'             WHERE module = 'igm_footer' AND name = 'x_footer_block';
UPDATE ir_model_data SET name = 'external_layout_standard_igm' WHERE module = 'igm_footer' AND name = 'external_layout_standard_x';
UPDATE ir_model_data SET name = 'external_layout_boxed_igm'    WHERE module = 'igm_footer' AND name = 'external_layout_boxed_x';
UPDATE ir_model_data SET name = 'external_layout_bold_igm'     WHERE module = 'igm_footer' AND name = 'external_layout_bold_x';
UPDATE ir_model_data SET name = 'external_layout_striped_igm'  WHERE module = 'igm_footer' AND name = 'external_layout_striped_x';
UPDATE ir_model_data SET name = 'external_layout_din5008_igm'  WHERE module = 'igm_footer' AND name = 'external_layout_din5008_x';

-- igm_task_forecast: cron (noupdate -> preserves the tuned schedule) + settings view
UPDATE ir_model_data SET name = 'ir_cron_igm_task_forecast'                  WHERE module = 'igm_task_forecast' AND name = 'ir_cron_x_task_forecast';
UPDATE ir_model_data SET name = 'res_config_settings_view_form_igm_forecast' WHERE module = 'igm_task_forecast' AND name = 'res_config_settings_view_form_x_forecast';

-- igm_employee_dashboard: model, view, menu, ACL
UPDATE ir_model_data SET name = 'model_igm_employee_dashboard'    WHERE module = 'igm_employee_dashboard' AND name = 'model_x_employee_dashboard';
UPDATE ir_model_data SET name = 'view_igm_employee_dashboard_form' WHERE module = 'igm_employee_dashboard' AND name = 'view_x_employee_dashboard_form';
UPDATE ir_model_data SET name = 'menu_igm_employee_dashboard_root' WHERE module = 'igm_employee_dashboard' AND name = 'menu_x_employee_dashboard_root';
UPDATE ir_model_data SET name = 'access_igm_employee_dashboard_user' WHERE module = 'igm_employee_dashboard' AND name = 'access_x_employee_dashboard_user';

-- ============================================================
-- 4. Model rename: x.employee.dashboard -> igm.employee.dashboard
-- ============================================================
UPDATE ir_model        SET model = 'igm.employee.dashboard' WHERE model = 'x.employee.dashboard';
UPDATE ir_model_fields SET model = 'igm.employee.dashboard' WHERE model = 'x.employee.dashboard';
-- Transient model's table (holds the stored `name` field; x_field_service_count is computed/unstored -> no column)
ALTER TABLE IF EXISTS x_employee_dashboard RENAME TO igm_employee_dashboard;

-- ============================================================
-- 5. Field metadata (ir_model_fields.name)
-- ============================================================
UPDATE ir_model_fields SET name = replace(name, 'x_footer_',   'igm_footer_')   WHERE model = 'res.company'         AND name LIKE 'x_footer_%';
UPDATE ir_model_fields SET name = replace(name, 'x_footer_',   'igm_footer_')   WHERE model = 'res.config.settings' AND name LIKE 'x_footer_%';
UPDATE ir_model_fields SET name = replace(name, 'x_forecast_', 'igm_forecast_') WHERE model = 'res.company'         AND name LIKE 'x_forecast_%';
UPDATE ir_model_fields SET name = replace(name, 'x_forecast_', 'igm_forecast_') WHERE model = 'res.config.settings' AND name LIKE 'x_forecast_%';
UPDATE ir_model_fields SET name = 'igm_field_service_count' WHERE model = 'igm.employee.dashboard' AND name = 'x_field_service_count';

-- ============================================================
-- 6. Stored columns on res_company (the actual data)
-- ============================================================
ALTER TABLE res_company RENAME COLUMN x_footer_enabled        TO igm_footer_enabled;
ALTER TABLE res_company RENAME COLUMN x_footer_manager        TO igm_footer_manager;
ALTER TABLE res_company RENAME COLUMN x_footer_phone          TO igm_footer_phone;
ALTER TABLE res_company RENAME COLUMN x_footer_fax            TO igm_footer_fax;
ALTER TABLE res_company RENAME COLUMN x_footer_email          TO igm_footer_email;
ALTER TABLE res_company RENAME COLUMN x_footer_seat           TO igm_footer_seat;
ALTER TABLE res_company RENAME COLUMN x_footer_register_court TO igm_footer_register_court;
ALTER TABLE res_company RENAME COLUMN x_footer_registry       TO igm_footer_registry;
ALTER TABLE res_company RENAME COLUMN x_footer_tax_number     TO igm_footer_tax_number;
ALTER TABLE res_company RENAME COLUMN x_footer_vat            TO igm_footer_vat;
ALTER TABLE res_company RENAME COLUMN x_footer_bank_name      TO igm_footer_bank_name;
ALTER TABLE res_company RENAME COLUMN x_footer_iban           TO igm_footer_iban;
ALTER TABLE res_company RENAME COLUMN x_footer_bic            TO igm_footer_bic;

ALTER TABLE res_company RENAME COLUMN x_forecast_enabled       TO igm_forecast_enabled;
ALTER TABLE res_company RENAME COLUMN x_forecast_horizon_days  TO igm_forecast_horizon_days;
ALTER TABLE res_company RENAME COLUMN x_forecast_skip_holidays TO igm_forecast_skip_holidays;

COMMIT;
