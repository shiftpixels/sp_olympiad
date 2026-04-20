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
