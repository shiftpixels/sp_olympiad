# SP_Olympiad — Task List (Odoo 19)

> **Updated for Odoo 19 compliance**  
> All implementations must follow Odoo 19 conventions.

## Phase 1: Docker Dev Environment
- [x] Create `docker-compose.yml` (odoo:19.0 + postgres:16 + pgadmin)
- [x] Create `odoo.conf` (dev_mode, addons_path)
- [x] Create `addons/` folder structure (6 module placeholders)
- [x] Start and verify → `http://localhost:8069`

## Phase 2: `sp_olympiad_core`
- [x] Module scaffold (`__manifest__.py`, `__init__.py`, folder structure)
- [ ] `sp_olympiad.event` model
  - [ ] Base: name, year, code_prefix, state, date_start, date_end
  - [ ] Accommodation: accommodation_ids (One2many → sp_olympiad.event.accommodation)
  - [ ] Pricing: registration_fee, accommodation_fee, excursion_fee + currency_id
  - [ ] Deadlines & Venue: research_paper_deadline, venue_name
  - [ ] Medal thresholds: medal_gold_min, medal_silver_min, medal_bronze_min, medal_hm_min
  - [ ] Age group boundaries: age_junior_min/max, age_senior_min/max
  - [ ] Config: min_jury_per_project, best_stand_max_score
- [ ] `sp_olympiad.event.accommodation` model (date, label, sequence)
- [ ] `sp_olympiad.category` model + seed data (7 categories)
- [ ] `sp_olympiad.project` model
  - [ ] Core fields + state Selection
  - [ ] `_compute_code` → `{code_prefix}{year}-{cat_code}-{seq:03d}`
  - [ ] `_compute_total` → uses event pricing fields
  - [ ] `_compute_medal` → uses event.medal_*_min thresholds
  - [ ] `_compute_age_group` → max(student.age) vs event age boundaries
  - [ ] `_compute_score` → average of jury scores
  - [ ] Add `mail.thread` + `mail.activity.mixin`
- [ ] `sp_olympiad.student` model
  - [ ] Core fields (first_name, last_name, birth_date, gender, country_id)
  - [ ] `accommodation_ids` (Many2many → sp_olympiad.event.accommodation) - **renamed for consistency**
  - [ ] `_compute_age`, `_compute_nights`, `_compute_name`
  - [ ] `no_accommodation` (Boolean) — when True, accommodation is ignored
- [ ] Security setup (Odoo 19 3-tier):
  - [ ] `ir.module.category` -> `res.groups.privilege` -> `res.groups`
  - [ ] Groups: `group_sp_olympiad_mentor`, `group_sp_olympiad_jury`, `group_sp_olympiad_admin`
  - **Note:** Group names follow pattern `sp_olympiad_<role>` (e.g., `sp_olympiad_user`, `sp_olympiad_jury`, `sp_olympiad_admin`)
- [ ] `ir.model.access.csv` + record rules
- [ ] `res.config.settings`: verify_base_url, sp_olympiad_logo

### Odoo 19 Compliance Notes
- Use `<list>` instead of `<tree>` in XML views
- Use `invisible="..."` instead of `attrs="{'invisible': [...]}"`
- Use `@api.ondelete(at_uninstall=False)` instead of overriding `unlink()`
- Use `models.Constraint` instead of `_sql_constraints`
- Use `@api.private` decorator for internal methods
- Use `_read_group()` or `formatted_read_group()` instead of `read_group()`

## Phase 2.5: Stripe Payment Setup
- [ ] Install `payment` + `payment_stripe` standard Odoo modules
- [ ] Configure Stripe provider in `payment.provider` (test mode → live mode)
- [ ] Set `payment.provider` with `code='stripe'` + API keys via `res.config.settings`

## Phase 3: `sp_olympiad_mentor`
- [ ] Mentor self-registration flow (portal)
- [ ] 5-step project registration wizard
  - [ ] Step 1: Category + participant count
  - [ ] Step 2: Student details (dynamic one2many)
  - [ ] Step 3: Project details + abstract upload
  - [ ] Step 4: Accommodation (nights from event.accommodation_ids)
  - [ ] Step 5: Payment via Stripe → Submit (enabled after payment confirmation)
- [ ] Stripe payment transaction linked to `sp_olympiad.project`
  - [ ] `payment_tx_id` (Many2one → `payment.transaction`) on `sp_olympiad.project`
  - [ ] Payment callback: on `state='done'` → set `project.paid=True`
- [ ] Research paper upload action (deadline check via event.research_paper_deadline)
- [ ] Mentor dashboard view
- [ ] Email templates: Registration Confirmation, Payment Confirmation, Research Paper Reminder

## Phase 4: `sp_olympiad_jury`
- [ ] `sp_olympiad.criterion` model
  - [ ] name, category_id, max_score, weight, sequence, apply_age_group
  - [ ] `is_reference` (Boolean) — Quelle/References flag
  - [ ] `excluded_category_ids` (Many2many → sp_olympiad.category)
  - [ ] `@api.constrains` → SUM(weight) per category == 1.0
- [ ] `sp_olympiad.jury.member` model (partner_id, user_id, title, category_ids, jury_lang, project_ids)
- [ ] `sp_olympiad.jury.score` model + `_compute_weighted_score` + `mail.thread`
- [ ] Project assignment view (manual + auto-filter: category + language)
- [ ] Scoring form with slider UI (0–max per criterion)

## Phase 5: `sp_olympiad_admin`
- [ ] Admin panel with 6-tab notebook
  - [ ] Tab 1: All Projects
  - [ ] Tab 2: Mentors (revenue summary)
  - [ ] Tab 3: Jury Management + Coverage Report (vs event.min_jury_per_project)
  - [ ] Tab 4: Standings + Publish button
  - [ ] Tab 5: Best Stand results (Junior / Senior)
  - [ ] Tab 6: CSV Exports
- [ ] Workflow: `draft → submitted → paid → evaluated → published`
- [ ] 5 CSV export actions
- [ ] Email templates: Jury Assignment, Results Published, Certificate Ready

## Phase 6: `sp_olympiad_reports`
- [ ] Visa Letter QWeb PDF (uses event.venue_name, settings.verify_base_url)
- [ ] Certificate PDFs — 5 types (Gold / Silver / Bronze / HM / Participation)
- [ ] QR code generation (`python-qrcode` → base64)
- [ ] Bulk print batch action

## Phase 7: `sp_olympiad_vote`
- [ ] `sp_olympiad.stand.vote` model
  - [ ] score: 0 – event.best_stand_max_score
  - [ ] ip_address: `Char(45)`, fingerprint: `Char(64)`
  - [ ] `models.Constraint`: `UNIQUE(project_id, ip_address)`
- [ ] Public voting controller (no login)
- [ ] JS fingerprint: SHA-256(userAgent + screenRes + timezone + language)
- [ ] Junior & Senior separate results
- [ ] Admin live results dashboard

## Phase 8: i18n
- [ ] English base language
- [ ] German `.po` translation files for all modules

## Phase 9: Testing & Verification
- [ ] Install all modules sequentially via Docker exec
- [ ] Full end-to-end test per role (Mentor, Jury, Admin, Public)
- [ ] PDF output + QR code validation
- [ ] CSV export integrity check
- [ ] Email template trigger tests

---

## Odoo 19 Key Changes Reference

| Change | Old (Odoo 17-) | New (Odoo 19) |
|--------|----------------|---------------|
| List view tag | `<tree>` | `<list>` |
| Dynamic attributes | `attrs="{'invisible': [...]}"` | `invisible="..."` (direct) |
| Delete validation | Override `unlink()` | `@api.ondelete(at_uninstall=False)` |
| SQL Constraints | `_sql_constraints` | `models.Constraint(...)` |
| Security Groups | `category_id` on `res.groups` | `privilege_id` + `res.groups.privilege` |
| QWeb Variables | `t-esc` | `t-out` (t-esc deprecated) |
| Private Methods | `_` prefix | `@api.private` decorator |
| Aggregation | `read_group()` | `_read_group()` or `formatted_read_group()` |

---

*This task list is based on the data models in `data_models.md` and follows Odoo 19 development standards.*
