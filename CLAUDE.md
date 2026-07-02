# Odoo Project Context & Guidelines

## 1. Environment & Architecture

- **Odoo Version**: 18.0 — CE core + Enterprise addons.
- **Paths** (relative to this workspace root):
  - `odoo/addons/` — framework core (base, web, …)
  - `addons/` — Odoo **CE** modules
  - `addons_ee/` — **Enterprise** modules (git submodule)
  - `addons_igm/` — **our custom modules** (the custom entry on `addons_path`)
  - `igm_tools/` — operational PowerShell scripts + `master_data/` (NOT Odoo modules)
- **Config**: `odoo_local.conf` · **DB**: `odoo_v18_2026_06_11_skr03` · **Postgres**: `localhost:5432` (user/pw `odoo`/`odoo`)
- **Runtime**: launched via the **VSCode Python debugger** using the **venv** interpreter
  `.venv\Scripts\python.exe odoo-bin -c odoo_local.conf --dev=all` (Windows / PowerShell).
- **Convention over Configuration.** Never modify core; always extend via `_inherit`.

## 2. Mandatory Rules for AI Code Generation

### A. Core Strategy (Strict Lookup) — most important rule
- **Standard-first is ALWAYS prio 1.** Before proposing or building any custom model, field, or
  flag, first find a **standard Odoo model — or a combination of standard models — that already
  fulfils the goal**, and suggest that solution first. Only fall back to a custom model when no
  standard combination fits, and say explicitly why the standard options were rejected. Reuse the
  hierarchy/relations the target model already ships (e.g. `res.partner` `parent_id`/`child_ids` +
  `type='other'` for physical sub-locations) before inventing a parallel structure. A field-only
  `_inherit` on a standard model beats a new model (no new ACL, no record-ownership coupling).
- Before writing **any** model field, XML view, security rule, or data record, **look up the
  matching pattern in the core source** (`odoo/addons/`, `addons/`, `addons_ee/`) **for this exact
  version**. Field names, framework methods, view structure, and the XML data-eval context change
  between versions — verify, never assume from memory.
- Lessons that prove why: the active report layout is **`l10n_din5008`** (its own footer, not the
  standard `external_layout_*`); `ir.cron` dropped `numbercall`/`doall` and `nextcall` defaults to
  now; in XML `eval`, `datetime` is bound to the **class** (use `datetime.now()`, or omit and rely
  on defaults).
- **CE/EE mismatch caveat**: CE core is paired with a possibly-different EE submodule version. Do
  **not** assume an EE module's expected method exists in CE (e.g. `sale_subscription` calls
  `_sale_order_get_page_view_values`, absent in CE `sale` → portal 500). Verify cross-module calls.

### B. Python Models & Data
- Always set `_description` on a new `models.Model`.
- Prefer computed fields with `@api.depends` over `@api.onchange`.
- Enforce business logic with `@api.constrains`, not silent exceptions.
- Wrap user-facing strings in `_("...")`.
- PEP 8, max line width **120**.
- **Prefix**: custom models/fields use the group prefix **`igm_`** (models `igm.<name>`, fields
  `igm_<name>`). **Never use `x_`** — it is reserved by Odoo Studio for UI-created fields/models.
  Display names and content (e.g. a person's name) are NOT prefixes and stay as-is.
- **Display-name tagging**: tag the names of **admin-facing** records (Scheduled Actions, Server
  Actions, Automated Actions, technical menu items) with a readable **`[IGM]`** label, e.g.
  `[IGM] Generate Recurring Task Forecast`, so they are scannable among the many standard records.
  Use the bracket label, NOT the snake_case `igm_`, for display text. **Never tag end-user-facing
  strings** (button labels, customer-visible menus, report/footer text, field labels) — keep those
  natural and translatable.
- **Placement**: every custom module goes in `addons_igm/`, named with the `igm_` prefix.
- **App icon**: every custom app uses the IGM logo. Copy the master
  `igm_tools/branding/igm_app_icon.png` to the module's `static/description/icon.png` (that's the
  file Odoo shows as the Apps tile). Point any settings `<app logo="...">` at the module's own
  `/<module>/static/description/icon.png`.

### C. UI & XML Views
- Inherit views with explicit `<xpath>` on `field`/`button` attributes (`name=…`, `hasclass(…)`),
  never absolute positions.
- Structure: forms, lists, kanban; clear actions; explicit `<menuitem>` chains ordered by `sequence`.
- Reports: inherit the **active** external layout for this DB (`l10n_din5008`), not only the
  generic `external_layout_*` templates.

### D. Security & Permissions ("Never Forget")
- Every **newly created** model gets an entry in `security/ir.model.access.csv`.
  (Pure `_inherit` of an existing model needs no new ACL.)
- Define groups and record rules in `security/security_rules.xml`.
- `__manifest__.py` load order: **security files load before view XMLs**.

### E. New Apps / Modules — Start From What Already Exists
- **Copy the local pattern first.** Before scaffolding a new app, read a comparable module already
  in `addons_igm/` and mirror its layout, manifest shape, and naming — do not invent structure from
  scratch. Good references by shape:
  - full business app (models + views + security + data): `igm_fsm/`, `igm_task_forecast/`
  - OWL/JS frontend or PWA-style app (`static/src`, assets bundle): `igm_fsm_app/`,
    `igm_objektleiter_app/`
  - JSON/REST controllers for an external client: `igm_fsm_api/controllers/`
  - dashboard / employee-facing views: `igm_employee_dashboard/`
  - report / layout customization: `igm_footer/report/`
  - seed data + payroll-style config: `igm_de_minijob_payroll/data/`
- **Standard folder layout** (only the folders a module actually needs):
  `models/`, `views/`, `security/` (`ir.model.access.csv` + `security_rules.xml`), `data/`,
  `report/`, `controllers/`, `static/description/` (icon + index), `static/src/` (JS/CSS/OWL).
  Keep `models/__init__.py` and the package `__init__.py` importing submodules, exactly as the
  existing modules do.
- **Follow OCA community guidelines** for anything not covered locally: one model per file named
  after the model (`igm_<name>.py`), manifest keys in the conventional order
  (`name`, `version`, `summary`, `category`, `author`, `website`, `license`, `depends`, `data`,
  `assets`), semantic module `version` (`18.0.x.y.z`), explicit `license` (`LGPL-3`), views/data
  files grouped by type under `data`, and PEP 8 / Odoo linting. When our local convention and OCA
  disagree, the **rules in this file win** (e.g. `igm_` prefix, `[IGM]` admin tagging, IGM icon).
- Still obey the app rules above: `igm_` prefix (§B), ACL + record rules for every new model
  (§D above), the IGM app icon (§B), and `'application': True` so the tile appears.

### F. Scheduled Actions / Crons
- Declare `ir.cron` as XML data inside `<data noupdate="1">` so the schedule — tuned in the standard
  **Settings → Technical → Scheduled Actions** UI — survives module upgrades.
- Split config surfaces: behaviour that has no standard UI → a `res.config.settings` section;
  the run schedule → the standard Scheduled Actions UI (don't duplicate it).
- Omit `nextcall` (it defaults to now); never reference `datetime` in an XML `eval`.

## 3. Workflow Commands (Windows / venv / PowerShell)
- Install or test a module:
  `& .venv\Scripts\python.exe odoo-bin -c odoo_local.conf -d odoo_v18_2026_06_11_skr03 -i your_module --test-enable --stop-after-init`
- Scaffold a module skeleton:
  `& .venv\Scripts\python.exe odoo-bin scaffold your_module addons_igm`
- **Auto-apply verified modules (don't wait for the UI).** Once a new/changed custom module
  passes local checks (Python `py_compile` **and** XML parses clean), load it into the DB via CLI
  automatically — do **not** make the operator run **Apps → Update Apps List** by hand:
  - first-time install: `-i <module>` (this is what registers a brand-new module + its app tile;
    a `-u` on a not-yet-installed module is a no-op).
  - subsequent code/view/asset/data changes: `-u <module>` (upgrades in place).
  - always add `--stop-after-init`; set `'application': True` for the tile to appear.
  - The DB is single-writer while the **VSCode debugger holds it**, so this needs the debug
    session **stopped first**. Ask the user to stop it (or confirm it's stopped), run the
    `-i`/`-u` command, report the result, then the user restarts the debugger.
  - Example (first install):
    `& .venv\Scripts\python.exe odoo-bin -c odoo_local.conf -d odoo_v18_2026_06_11_skr03 -i your_module --stop-after-init`
- After code changes: **restart the VSCode debug session** (autoreload is off unless `watchdog`
  is installed).
- Module/prefix renames: prefer **files + SQL rename-in-place** (`ALTER … RENAME COLUMN`, `UPDATE`
  on `ir_model_fields`/`ir_model_data`/`ir_module_module`, `arch_db::text` replace) to preserve
  data; then restart to reload the registry.

## 4. Domain Notes
- Public holidays for task forecasting live in **Time Off → Public Holidays**
  (`resource.calendar.leaves` with `resource_id = False`); seed CSV in
  `igm_tools/master_data/`.
- End state should be **UI-native and handover-ready** for non-technical operators; scripts/CSVs
  are stopgaps, not the target.
