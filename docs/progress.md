# SP Olympiad - Module Functional Overview

This document describes what the `sp_olympiad` module currently provides from an end-user perspective.

## Current Scope

The module currently covers:
- Event management
- Category management
- Event accommodation date planning
- Website category pages
- Category criteria PDF export
- Olympiad general settings

The module does **not** yet include mentor registration, project submission flow, jury scoring workflow, payments, or final admin panel workflows.

## Backend Features

### 1. Olympiad Events
Model: `sp_olympiad.event`

Main capabilities:
- Create and manage events with:
  - Event name
  - Code prefix (max 5 chars)
  - Date range (`Dates`)
  - Status (`Draft`, `Active`, `Finished`, `Cancelled`)
- Link active categories to each event.
- Track changes through chatter/activity (`mail.thread`, `mail.activity.mixin`).

Key validations:
- Start date must be before or equal to end date.
- Event cannot be marked as `Finished` before end date has passed.

Views:
- Kanban view
- List view
- Form view with notebook tabs

### 2. Event Accommodation Dates
Model: `sp_olympiad.event.accommodation`

Main capabilities:
- Each event can hold multiple accommodation date entries.
- For each entry, admin can define:
  - `Date`
  - `Label` (short note, e.g. Arrival, Registration Desk, City Tour)
  - `Sequence`
- New entries default to the event start date.

UI behavior:
- Managed inside Event form under **Accommodation Dates** tab.
- Displayed as kanban-style cards for better readability.

### 3. Olympiad Categories
Model: `sp_olympiad.category`

Main capabilities:
- Create and manage categories with:
  - Name
  - Unique code
  - Max participants
  - Sort order (`sequence`)
  - Active/passive state
  - Image
  - Web description (HTML)
  - Evaluation criteria (HTML)
- Solo behavior is derived automatically (`is_solo = True` when `max_participants = 1`).
- Participant count is validated with:
  - Minimum: `1`
  - Maximum: controlled by system setting (**Category Max Participants Limit**).
- If a user enters a number above the configured maximum, the value is automatically reduced to the allowed limit before save.
- Field help text dynamically shows the currently configured system limit.

Views:
- Kanban view
- List view
- Form view (with separate tabs for description and criteria)

### 4. Settings
Model extension: `res.config.settings`

Main capability:
- Configure a global competition name:
  - `Competition Name` (`olympiad_name`)
- Configure category participant upper bound:
  - `Category Max Participants Limit` (`category_max_participants_limit`)
  - Used by category validation logic and UI help text.

Location:
- Olympiad > Configuration > General Settings

## Website Features

Public routes:
- `/olympiad/categories`
- `/olympiad/category/<category>`

What visitors can do:
- Browse active categories on a public categories page.
- Open category detail pages.
- See category image, description, and evaluation criteria.
- Download criteria as PDF from the category detail page.

## Reporting Features

Report action:
- **Evaluation Criteria** PDF for `sp_olympiad.category`

Current behavior:
- Generates category-specific criteria document.
- Includes custom paper format (A4 landscape, compact margins).
- Available from category-related actions and website detail page link.

## Navigation (Backend Menu)

Main menu:
- Olympiad

Submenus:
- Events
- Configuration
  - Categories
  - General Settings

## Access Overview (Current)

- Internal users (`base.group_user`): full CRUD on events and categories.
- Public/portal users: read access to categories.
- Accommodation model has internal-user access for management.

## Notes For Future User Guide

When this document is expanded into a full user guide, recommended sections are:
1. Event creation walkthrough
2. Category setup standards (naming, coding, ordering)
3. Accommodation date planning examples
4. Website content publishing flow
5. PDF criteria generation and usage
6. Role-based operations (admin vs internal users)

## Change Log

### 2026-04-25 - Restricted Mentor Access to Portal (Frontend Only)

- Summary:
  - Changed `sp_olympiad.group_sp_olympiad_mentor` to imply `base.group_portal` instead of `base.group_user`. Mentors can no longer access the Odoo Backend Dashboard (unless explicitly granted admin/staff privileges).
  - Explicitly granted `read` and `write` access for Mentors on `sp_olympiad.mentor` model via `access_sp_olympiad_mentor_self` since they lost `base.group_user` permissions.
  - Ran a manual SQL migration to clean up existing mentor users, removing them from the exclusive `Role / User` group and inserting them into `Role / Portal` to satisfy Odoo's disjoint group constraints.
- Files:
  - `addons_dev/sp_olympiad/security/sp_olympiad_security.xml`
- Why:
  - Isolate mentors completely from ERP backend menus (Discuss, Calendar, Contacts).
  - Provide a clean, restricted, and safe experience exclusively via the `/my/olympiad` portal route.
- Verification:
  - Odoo module upgraded successfully without XML parsing or Disjoint Group constraint errors.

### 2026-04-25 - Mentor to User Phone Number Synchronization

- Summary:
  - Updated `mentor_signup.py` to pass the `phone` field into the `res.users` creation dictionary so that the main user account also has the phone number stored.
  - Ran a data migration script via Odoo shell to sync the `phone` number of existing `sp_olympiad.mentor` records to their related `res.users` accounts.
- Files:
  - `addons_dev/sp_olympiad/controllers/mentor_signup.py`
- Why:
  - Ensure consistency between the mentor profile and the underlying user account data (similar to how email is synced).

### 2026-04-25 - Removed Redundant Fields from Mentor Model & Views

- Summary:
  - Removed `active` and `user_active` fields from `sp_olympiad.mentor` model and views.
  - Removed `action_activate` and `action_deactivate` methods.
  - Removed `verification_token` and `token_expiry` fields from the mentor form view as they are internal technical fields.
- Files:
  - `addons_dev/sp_olympiad/models/olympiad_mentor.py`
  - `addons_dev/sp_olympiad/views/mentor_views.xml`
- Why:
  - The `active` toggle on the mentor record was causing confusion and bypassed validation.
  - Verification tokens are internal UUIDs managed completely under the hood. Displaying them in the admin form adds unnecessary clutter and provides no value to the admin user.
- Verification:
  - Module updated and `sp_olympiad.field_sp_olympiad_mentor__active` was successfully dropped from the database.

### 2026-04-25 - Security Audit Remediation

- Summary:
  - Added missing `ir.rule` to `sp_olympiad.mentor` model to restrict mentors to viewing only their own profile data, preventing an IDOR vulnerability.
  - Removed write/create/unlink privileges from the Jury group for the Event Accommodation model in `ir.model.access.csv`, resolving a privilege escalation issue.
  - Added validation for `country_id` in the `mentor_signup` controller to ensure the country exists before record creation, preventing PostgreSQL 500 errors.
  - Implemented `@api.ondelete` guard in `OlympiadEventAccommodation` model to enforce data integrity by preventing deletion of past dates.
- Files:
  - `addons_dev/sp_olympiad/security/sp_olympiad_security.xml`
  - `addons_dev/sp_olympiad/security/ir.model.access.csv`
  - `addons_dev/sp_olympiad/controllers/mentor_signup.py`
  - `addons_dev/sp_olympiad/models/olympiad_event_accommodation.py`
- Why:
  - Fix high and medium severity security vulnerabilities identified in the recent codebase audit (IDOR, Privilege Escalation).
  - Align models with `GEMINI.md` architectural requirements for UI protection.
- Verification:
  - Code compiled and verified using `python3 -m compileall -q addons_dev/sp_olympiad`.

### 2026-04-22 - Mentor Auth Anti-Enumeration and Login Message Hardening

- Summary:
  - Added a `/web/login` controller override to replace specific login failures with a single generic security-safe message.
  - Added shared in-module rate limiting utilities (IP + email buckets) and applied them to mentor `signup`, `resend verification`, and login attempts.
  - Removed email-enumerating signup responses (`email already registered`) and replaced them with neutral success messaging.
  - Updated resend-verification behavior to return neutral responses regardless of account existence, while still sending mail for eligible unverified mentors.
- Files:
  - `addons_dev/sp_olympiad/controllers/auth_security.py`
  - `addons_dev/sp_olympiad/controllers/mentor_signup.py`
  - `addons_dev/sp_olympiad/controllers/__init__.py`
  - `addons_dev/sp_olympiad/utils/__init__.py`
  - `addons_dev/sp_olympiad/utils/security_rate_limit.py`
  - `addons_dev/sp_olympiad/docs/progress.md`
- Why:
  - Reduce account enumeration risk in public auth flows.
  - Keep login failures non-attributable (wrong password vs unverified vs inactive).
  - Slow down brute-force and verification-email abuse attempts with practical per-window throttling.
- Verification:
  - `PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m compileall -q addons_dev/sp_olympiad`
  - `git -C addons_dev/sp_olympiad diff -- controllers/mentor_signup.py controllers/auth_security.py utils/security_rate_limit.py`

### 2026-04-22 - Mentor Signup Verification/Login Enforcement (Odoo 19)

- Summary:
  - Refactored mentor signup user creation to use `no_reset_password=True` so unverified users can be created with `active=False` without `auth_signup` archived-user side effects.
  - Removed debug-only mentor user route from public controller.
  - Aligned `res.users._check_credentials` override with Odoo 19 signature and switched to `AccessDenied` for standard authentication blocking.
  - Replaced `groups_id` usages with Odoo 19-compatible `group_ids` in mentor signup/verification role assignment.
  - Restricted `/my/olympiad` dashboard route to verified mentors (or system admins) instead of any authenticated user.
  - Kept mentor login blocked until email verification is completed.
- Files:
  - `addons_dev/sp_olympiad/controllers/mentor_signup.py`
  - `addons_dev/sp_olympiad/controllers/main.py`
  - `addons_dev/sp_olympiad/models/olympiad_mentor.py`
  - `addons_dev/sp_olympiad/models/res_users.py`
  - `addons_dev/sp_olympiad/docs/progress.md`
- Why:
  - Ensure mentors cannot log in before email verification and keep behavior compatible with Odoo 19 authentication flow.
- Verification:
  - `PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m compileall -q addons_dev/sp_olympiad`
  - `docker compose exec odoo19 bash -lc "odoo -d odoo_19 -u sp_olympiad --stop-after-init --db_host=db --db_user=odoo --db_password='odoo19@2025'"`
  - `docker compose exec odoo19 bash -lc "odoo shell -d odoo_19 --db_host=db --db_user=odoo --db_password='odoo19@2025' <<'PY' ... create unverified mentor and assert authenticate raises AccessDenied ... PY"`
  - `docker compose exec odoo19 bash -lc "odoo shell -d odoo_19 --db_host=db --db_user=odoo --db_password='odoo19@2025' <<'PY' ... deactivate existing unverified mentors with active users ... PY"` (result: `mentor_ids_to_fix=[2]`)

### 2026-04-21 - Block Mentor Login Until Email Verification

- Summary:
  - Updated mentor signup flow so users created with email verification enabled stay inactive until they verify.
  - Updated mentor verification logic to activate the linked user and grant mentor group only after successful token verification.
- Files:
  - `addons_dev/sp_olympiad/controllers/mentor_signup.py`
  - `addons_dev/sp_olympiad/models/olympiad_mentor.py`
  - `addons_dev/sp_olympiad/docs/progress.md`
- Why:
  - Prevent mentors from logging in before email ownership is confirmed.
- Verification:
  - `PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m compileall -q addons_dev/sp_olympiad`
  - `docker compose exec odoo19 bash -lc "odoo -d odoo_19 -u sp_olympiad --stop-after-init --db_host=db --db_user=odoo --db_password='odoo19@2025'"`
  - `docker compose exec odoo19 bash -lc "odoo shell -d odoo_19 --db_host=db --db_user=odoo --db_password='odoo19@2025' <<'PY' ... deactivate unverified mentor users ... PY"` (result: `deactivated_users=1`)

### 2026-04-21 - Mentor Signup Hardening and Runtime Fixes

- Summary:
  - Hardened mentor signup endpoints with CSRF protection and savepoint rollback to prevent partial account creation.
  - Applied mentor signup and verification settings in controller flow.
  - Restored missing website dashboard route registration by importing `controllers/main.py`.
  - Added missing mentor verification email template and wired it into module data.
  - Fixed country re-selection behavior after form validation errors.
- Files:
  - `addons_dev/sp_olympiad/controllers/mentor_signup.py`
  - `addons_dev/sp_olympiad/controllers/__init__.py`
  - `addons_dev/sp_olympiad/views/website_templates.xml`
  - `addons_dev/sp_olympiad/views/mentor_email_template.xml`
  - `addons_dev/sp_olympiad/__manifest__.py`
  - `addons_dev/sp_olympiad/docs/progress.md`
- Why:
  - Close security and reliability gaps in public mentor signup endpoints.
  - Ensure settings in General Settings have real runtime effect.
  - Prevent silent verification-email no-op caused by missing template data.
- Verification:
  - `PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m compileall -q addons_dev/sp_olympiad`
  - `docker compose exec odoo19 bash -lc "odoo -d odoo_19 -u sp_olympiad --stop-after-init --db_host=db --db_user=odoo --db_password='odoo19@2025'"`
  - `rg -n "csrf=False|savepoint|mentor_signup_enabled|mentor_verification_enabled" addons_dev/sp_olympiad/controllers/mentor_signup.py -S`
  - `rg -n "from \\. import main|from \\. import mentor_signup" addons_dev/sp_olympiad/controllers/__init__.py -S`
  - `rg -n "mentor_verification_email_template|mentor_email_template.xml" addons_dev/sp_olympiad/__manifest__.py addons_dev/sp_olympiad/views/mentor_email_template.xml -S`

### 2026-04-21 - Split-Ready Architecture Planning (No Functional Change)

- Summary:
  - Added a technical boundary plan for future addon extraction while keeping all current development in `sp_olympiad`.
- Files:
  - `addons_dev/sp_olympiad/docs/split_ready_plan.md`
  - `addons_dev/sp_olympiad/docs/progress.md`
- Why:
  - Preserve current module stability and velocity.
  - Keep payment/certification code extractable for future commercial packaging.
- Verification:
  - Documentation-only update; no model/view/security/runtime behavior changed.

### 2026-04-21 - Imported Planning Notes Into Module Docs (No Functional Change)

- Summary:
  - Copied planning notes from `.claude/odoo_addons/sp_olympiad` into module docs for centralized tracking.
  - Added a planning README to mark these as backlog references, not auto-applied work.
- Files:
  - `addons_dev/sp_olympiad/docs/planning/task.md`
  - `addons_dev/sp_olympiad/docs/planning/implementation_plan.md`
  - `addons_dev/sp_olympiad/docs/planning/data_models.md`
  - `addons_dev/sp_olympiad/docs/planning/README.md`
  - `addons_dev/sp_olympiad/docs/progress.md`
- Why:
  - Keep planning context inside the module repository.
  - Support step-by-step execution without applying full scope at once.
- Verification:
  - Documentation-only update; no module code, views, security, or runtime logic changed.

### 2026-04-21 - Removed Legacy `sp_olympiad_core` Runtime References

- Summary:
  - Removed old `sp_olympiad_core` external ID/module references from runtime code and views.
  - Standardized active module references to `sp_olympiad` since no backward compatibility is required before first release.
- Files:
  - `addons_dev/sp_olympiad/controllers/main.py`
  - `addons_dev/sp_olympiad/views/olympiad_category_reports.xml`
  - `addons_dev/sp_olympiad/views/website_templates.xml`
  - `addons_dev/sp_olympiad/views/res_config_settings_views.xml`
  - `addons_dev/sp_olympiad/models/res_config_settings.py`
  - `addons_dev/sp_olympiad/docs/progress.md`
- Why:
  - Prevent runtime template/report/action resolution errors caused by stale legacy module prefixes.
  - Keep module identity consistent across controller, report, website, and settings layers.
- Verification:
  - `rg -n "sp_olympiad_core" addons_dev/sp_olympiad` now returns matches only in planning docs under `docs/planning/`.
  - `python3 -m compileall -q addons_dev/sp_olympiad` completed without errors.

### 2026-04-21 - Removed `_sql_constraints` and `t-esc` Usage

- Summary:
  - Replaced category SQL constraint declaration with Python constraint validation.
  - Replaced website template `t-esc` usages with `t-out`.
- Files:
  - `addons_dev/sp_olympiad/models/olympiad_category.py`
  - `addons_dev/sp_olympiad/views/website_templates.xml`
  - `addons_dev/sp_olympiad/docs/progress.md`
- Why:
  - Align implementation with adopted Odoo 19 coding rules in this project (`_sql_constraints` and `t-esc` are avoided).
- Verification:
  - `rg -n "_sql_constraints|t-esc" addons_dev/sp_olympiad` now returns matches only in planning docs under `docs/planning/`.
  - `python3 -m compileall -q addons_dev/sp_olympiad` completed without errors.

### 2026-04-21 - Evaluation Criteria PDF Set Back To Portrait

- Summary:
  - Changed Evaluation Criteria report paper format orientation from landscape to portrait.
- Files:
  - `addons_dev/sp_olympiad/views/olympiad_category_reports.xml`
  - `addons_dev/sp_olympiad/docs/progress.md`
- Why:
  - Restore previous vertical PDF layout expected in user flow.
- Verification:
  - Ran module upgrade: `docker compose exec odoo19 odoo -d odoo_19 -u sp_olympiad --stop-after-init --db_host=db --db_user=odoo --db_password='odoo19@2025'`
  - Upgrade completed successfully.

### 2026-04-21 - Removed Company Header From Evaluation Criteria PDF

- Summary:
  - Removed default company header block (`My Company`, address) from the Evaluation Criteria PDF template.
- Files:
  - `addons_dev/sp_olympiad/views/olympiad_category_reports.xml`
  - `addons_dev/sp_olympiad/docs/progress.md`
- Why:
  - Keep the criteria document clean and content-focused without default external report header data.
- Verification:
  - Template layout call switched from `web.external_layout` to `web.basic_layout`.
  - Module upgrade should be run manually after this change.

### 2026-04-21 - Improved Word Table Fit for Evaluation Criteria PDF

- Summary:
  - Updated report CSS so Word-pasted tables fit page width more reliably and preserve consistent multi-page behavior.
  - Added header-row repeat support across PDF page breaks.
- Files:
  - `addons_dev/sp_olympiad/views/olympiad_category_reports.xml`
  - `addons_dev/sp_olympiad/docs/progress.md`
- Why:
  - Prevent overflow and inconsistent rendering when category criteria content includes rich tables from Word.
- Verification:
  - CSS now enforces `width/max-width: 100%`, `table-layout: fixed`, `thead` as `table-header-group`, and stronger cell wrapping rules.
  - Module upgrade should be run manually after this change.

### 2026-04-21 - Category Visibility and Deletion Guard

- Summary:
  - Confirmed website categories page publishes only active categories.
  - Added deletion guard to block removing categories that are already linked to any event.
- Files:
  - `addons_dev/sp_olympiad/models/olympiad_category.py`
  - `addons_dev/sp_olympiad/controllers/main.py`
  - `addons_dev/sp_olympiad/docs/progress.md`
- Why:
  - Keep public website aligned with active/passive category toggle.
  - Prevent data integrity issues by disallowing deletion of categories referenced by events.
- Verification:
  - Controller uses active-only domain: `[('active', '=', True)]` for `/olympiad/categories`.
  - Added `@api.ondelete(at_uninstall=False)` guard with linked-event check.
  - `python3 -m compileall -q addons_dev/sp_olympiad/models/olympiad_category.py` completed without errors.

### 2026-04-21 - Strengthened Category Deletion Guard For Event Links

- Summary:
  - Replaced previous delete guard implementation with a strict `unlink()` pre-check.
  - Category deletion is now blocked if the category is linked to any event (including inactive context).
- Files:
  - `addons_dev/sp_olympiad/models/olympiad_category.py`
  - `addons_dev/sp_olympiad/docs/progress.md`
- Why:
  - User validation showed category deletion was still possible despite event linkage.
  - `unlink()` pre-check ensures guard executes before deletion completes.
- Verification:
  - `python3 -m compileall -q addons_dev/sp_olympiad/models/olympiad_category.py` completed without errors.

### 2026-04-21 - UI-Level Delete Disable For Event-Linked Categories

- Summary:
  - Disabled default category delete action from the form and access rights.
  - Added a conditional custom delete button that appears only when category is not linked to any event.
  - Added warning message in form when category is event-linked.
- Files:
  - `addons_dev/sp_olympiad/models/olympiad_category.py`
  - `addons_dev/sp_olympiad/views/olympiad_category_views.xml`
  - `addons_dev/sp_olympiad/security/ir.model.access.csv`
  - `addons_dev/sp_olympiad/docs/progress.md`
- Why:
  - Prevent users from reaching destructive delete confirmation for categories already used in events.
  - Align UI behavior with business rule: linked categories are archive-only.
- Verification:
  - Category ACL unlink permission set to `0` for internal users.
  - Form has `delete="0"` and conditional object button `action_delete_if_unused`.
  - `python3 -m compileall -q addons_dev/sp_olympiad/models/olympiad_category.py` completed without errors.

### 2026-04-21 - Easier Access To Archived Categories

- Summary:
  - Added a dedicated backend menu entry for archived categories.
  - Added a dedicated action that opens categories with `active=False` directly.
- Files:
  - `addons_dev/sp_olympiad/views/olympiad_category_views.xml`
  - `addons_dev/sp_olympiad/views/menu_views.xml`
  - `addons_dev/sp_olympiad/docs/progress.md`
- Why:
  - Improve discoverability for general users who may not use advanced filter/search controls.
- Verification:
  - New action `action_olympiad_category_archived` uses domain `[('active', '=', False)]` with `active_test=False`.
  - New menu `Olympiad > Configuration > Archived Categories` points to this action.

### 2026-04-21 - Show Active And Passive Categories In Main List

- Summary:
  - Updated main Categories action to show both active and passive records by default.
- Files:
  - `addons_dev/sp_olympiad/views/olympiad_category_views.xml`
  - `addons_dev/sp_olympiad/docs/progress.md`
- Why:
  - In this project, archived categories are effectively passive categories and should be visible directly in the main list.
- Verification:
  - Main action `action_olympiad_category` now uses context `{'active_test': False}`.

### 2026-04-21 - Removed Separate Archived Categories Menu

- Summary:
  - Removed dedicated `Archived Categories` menu and its standalone action.
  - Kept unified category management in the main `Categories` screen.
- Files:
  - `addons_dev/sp_olympiad/views/menu_views.xml`
  - `addons_dev/sp_olympiad/views/olympiad_category_views.xml`
  - `addons_dev/sp_olympiad/docs/progress.md`
- Why:
  - Separate archived menu is unnecessary once main category list already shows both active and passive records.
- Verification:
  - `menu_olympiad_category_archived` removed.
  - `action_olympiad_category_archived` removed.

### 2026-04-21 - Hotfix For Category Form OwlError

- Summary:
  - Removed dynamic view conditions that referenced `is_used_in_event` on category form to stop Owl parse crash.
  - Kept server-side delete protection (`action_delete_if_unused` + `unlink` guard).
- Files:
  - `addons_dev/sp_olympiad/views/olympiad_category_views.xml`
  - `addons_dev/sp_olympiad/docs/progress.md`
- Why:
  - Category form was crashing with `field is undefined` in Owl lifecycle, blocking access to category records.
- Verification:
  - View no longer uses `is_used_in_event` in `invisible` expressions.
  - Delete restriction remains enforced server-side for event-linked categories.

### 2026-04-21 - Removed Category Form Delete Button For Consistent UX

- Summary:
  - Removed custom `Delete` button from category form.
  - Removed now-unused helper field/method related to conditional delete button visibility.
  - Kept server-side deletion block via `unlink()` for event-linked categories.
- Files:
  - `addons_dev/sp_olympiad/views/olympiad_category_views.xml`
  - `addons_dev/sp_olympiad/models/olympiad_category.py`
  - `addons_dev/sp_olympiad/docs/progress.md`
- Why:
  - Avoid contradictory UX where warning says “cannot be deleted” but a delete button is still shown.
- Verification:
  - No `action_delete_if_unused` or `is_used_in_event` usage remains in model/view.
  - `python3 -m compileall -q addons_dev/sp_olympiad/models/olympiad_category.py` completed without errors.

### 2026-04-21 - Replaced Category Warning Banner With Field Help

- Summary:
  - Removed always-visible warning banner from category form.
  - Added contextual help text directly on the `active` toggle field.
- Files:
  - `addons_dev/sp_olympiad/views/olympiad_category_views.xml`
  - `addons_dev/sp_olympiad/docs/progress.md`
- Why:
  - Keep UI cleaner while still explaining that `active=False` means archived/passive behavior.
- Verification:
  - Warning banner removed from form.
  - Help text is attached to `active` field in form view.
