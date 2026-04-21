# Architecture

This document describes the high-level architecture of the `sp_olympiad` module.

## Module Structure

```
sp_olympiad/
├── controllers/
│   └── main.py              # Website controllers for public routes
├── models/
│   ├── __init__.py
│   ├── olympiad_category.py    # Category model
│   ├── olympiad_event.py       # Event model
│   ├── olympiad_event_accommodation.py  # Accommodation dates
│   └── res_config_settings.py  # Settings extension
├── security/
│   ├── ir.model.access.csv    # Access control lists
│   └── sp_olympiad_security.xml  # User groups
├── views/
│   ├── olympiad_category_views.xml
│   ├── olympiad_category_reports.xml
│   ├── olympiad_event_views.xml
│   ├── res_config_settings_views.xml
│   ├── website_templates.xml
│   └── menu_views.xml
├── data/                      # Data files (if any)
├── static/
│   └── src/                   # Static assets (CSS, JS, images)
└── docs/
    ├── 01-architecture.md     # This file
    ├── 02-security.md
    ├── 03-users-and-groups.md
    ├── progress.md            # Change log
    └── planning/              # Backlog/planning notes
```

## Data Models

### sp_olympiad.event
Main event management model.

**Key fields:**
- `name` - Event name
- `code_prefix` - Short code (max 5 chars)
- `date_start`, `date_end` - Date range
- `state` - Status (Draft, Active, Finished, Cancelled)
- `category_ids` - One2many to categories

### sp_olympiad.event.accommodation
Accommodation date planning per event.

**Key fields:**
- `event_id` - Parent event
- `date` - Accommodation date
- `label` - Short note (e.g. Arrival, Registration)
- `sequence` - Order priority

### sp_olympiad.category
Competition categories.

**Key fields:**
- `name` - Category name
- `code` - Unique code
- `max_participants` - Max participants (1 = solo)
- `sequence` - Sort order
- `active` - Publish toggle
- `image` - Category image
- `description_web`, `criteria_html` - Web content

### sp_olympiad.res.config.settings
Settings extension for global configuration.

**Key fields:**
- `olympiad_name` - Competition name
- `category_max_participants_limit` - Max participants threshold

## Website Routes

| Route | Description | Access |
|-------|-------------|--------|
| `/olympiad/categories` | Public categories listing | Public |
| `/olympiad/category/<category>` | Category detail page | Public |

## Report Actions

| Report | Model | Format |
|--------|-------|--------|
| Evaluation Criteria | `sp_olympiad.category` | PDF |

## Configuration Menu

```
Olympiad
├── Events
├── Configuration
│   ├── Categories
│   └── General Settings
```

## Future Architecture Extensions

### Planned Models

| Model | Purpose | Status |
|-------|---------|--------|
| `sp_olympiad.project` | Project/submission management | Planned |
| `sp_olympiad.student` | Student records | Planned |
| `sp_olympiad.mentor` | Mentor profiles | Planned |
| `sp_olympiad.jury_assignment` | Jury-project assignment | Planned |
| `sp_olympiad.scoring` | Score entries | Planned |

### Module Split Strategy

For future commercial packaging:
- `sp_olympiad_core` - Free core features
- `sp_olympiad_payment` - Payment integration (extractable)
- `sp_olympiad_certification` - Certification (extractable)

See `docs/split_ready_plan.md` for details.
