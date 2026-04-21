# SP_Olympiad — Odoo 19 Data Models

> Field mapping from `prompt.md` data models to Odoo 19 conventions.  
> Includes field types, relationships, and computed fields.  
> **Updated for Odoo 19 compliance**

---

## General Rules

| Rule | Description |
|------|-------------|
| **Mentor** | Uses `res.users` + `res.partner` instead of a custom model (Odoo standard) |
| **Country** | `string` → `Many2one('res.country')` |
| **File** | `string` → `Binary` + separate `Char` (for filename) |
| **Nights** | `boolean[4]` → `Many2many('sp_olympiad.event.accommodation')` — dynamic per event |
| **Password** | Managed by `res.users`, not stored in custom models |
| **Sequence** | Auto project code via `ir.sequence` |

---

## New Model: `sp_olympiad.event`
*(not in prompt.md — added for year-based management)*

| Field | Odoo Field | Type | Notes |
|-------|------------|------|-------|
| id | id | Auto | |
| name | name | `Char` | e.g. "Innovate Germany 2027" |
| year | year | `Integer` | |
| code_prefix | code_prefix | `Char(size=4)` | "IG", "EURO", etc. |
| state | state | `Selection` | draft / open / closed / published |
| date_start | date_start | `Date` | |
| date_end | date_end | `Date` | |
| accommodation_ids | accommodation_ids | `One2many('sp_olympiad.event.accommodation','event_id')` | Accommodation dates for this event |
| **Pricing** | | | |
| registration_fee | registration_fee | `Float` | default=200.0 — per project |
| accommodation_fee | accommodation_fee | `Float` | default=50.0 — per person/night |
| excursion_fee | excursion_fee | `Float` | default=200.0 — per person |
| **Deadlines & Venue** | | | |
| research_paper_deadline | research_paper_deadline | `Date` | e.g. February 1 |
| venue_name | venue_name | `Char` | e.g. "Neue Birken Gasthaus" |
| **Medal Thresholds** | | | |
| medal_gold_min | medal_gold_min | `Integer` | default=91 |
| medal_silver_min | medal_silver_min | `Integer` | default=81 |
| medal_bronze_min | medal_bronze_min | `Integer` | default=65 |
| medal_hm_min | medal_hm_min | `Integer` | default=50 |
| **Jury Coverage** | | | |
| min_jury_per_project | min_jury_per_project | `Integer` | default=2 |
| **Best Stand Voting** | | | |
| best_stand_max_score | best_stand_max_score | `Integer` | default=10 |
| **Age Group Boundaries** | | | |
| age_junior_min | age_junior_min | `Integer` | default=12 |
| age_junior_max | age_junior_max | `Integer` | default=14 |
| age_senior_min | age_senior_min | `Integer` | default=15 |
| age_senior_max | age_senior_max | `Integer` | default=19 |
| **Currency** | | | |
| currency_id | currency_id | `Many2one('res.currency')` | default=EUR |

---

## New Model: `sp_olympiad.event.accommodation`
*(child of sp_olympiad.event — defines available accommodation dates)*

| Field | Odoo Field | Type | Notes |
|-------|------------|------|-------|
| id | id | Auto | |
| event_id | event_id | `Many2one('sp_olympiad.event')` | required, ondelete=cascade |
| date | date | `Date` | e.g. 2027-05-27 |
| label | label | `Char` | **Computed**: `@api.depends('date', 'event_id.date_start', 'event_id.date_end')` formats date range string (e.g., "Night of May 27–28, 2027") |
| sequence | sequence | `Integer` | display order |

> Admin defines the available nights when creating an event (e.g. 4 nights for one event, 2 for another).

---

## New Model: `sp_olympiad.category`
*(from prompt.md Section 4)*

| Field | Odoo Field | Type | Notes |
|-------|------------|------|-------|
| id | id | Auto | |
| name | name | `Char` | e.g. "Environmental Sciences & Chemistry" |
| code | code | `Char(size=3)` | ESC, EMP, HSB, ACR, GDD, ADD, CRW |
| max_participants | max_participants | `Integer` | default=3 |
| is_solo | is_solo | `Boolean` | True for ADD, CRW |
| description | description | `Text` | |

**Seed data:**
```
ESC, EMP, HSB, ACR, GDD → max=3, solo=False
ADD, CRW               → max=1, solo=True
```

---

## Mentor → `res.users` + `res.partner`

Mentors are Odoo users (self-register). `res.partner` already provides `name`, `email`, `country_id`.

| prompt.md | Odoo Field | Model | Type |
|-----------|------------|-------|------|
| firstName + lastName | name | `res.partner` | `Char` (combined) |
| birthDate | birthdate | `res.partner` | `Date` |
| country | country_id | `res.partner` | `Many2one('res.country')` |
| email | email | `res.partner` | `Char` |
| password | — | `res.users` | Managed by Odoo |

> `res.partner` gets an `is_sp_olympiad_mentor = Boolean` flag for filtering.

---

## `sp_olympiad.project`

| prompt.md | Odoo Field | Type | Notes |
|-----------|------------|------|-------|
| id | id | Auto | |
| code | code | `Char` | `_compute_code`, store=True |
| year | year | `Integer` | related: `event_id.year` |
| mentorId | mentor_id | `Many2one('res.users')` | domain: `groups=group_sp_olympiad_user` |
| name | name | `Char` | required |
| category | category_id | `Many2one('sp_olympiad.category')` | |
| presLang | pres_lang | `Selection` | [('en','English'),('de','German')] |
| excursion | excursion | `Boolean` | |
| abstractFile | abstract_file | `Binary` | |
| — | abstract_filename | `Char` | |
| researchPaper | research_paper | `Binary` | |
| — | research_paper_filename | `Char` | |
| paid | paid | `Boolean` | default=False, set True when payment.transaction state='done' |
| total | total_amount | `Float` | `_compute_total`, store=True |
| — | payment_tx_id | `Many2one('payment.transaction')` | Stripe transaction linked to this project |
| numS | num_students | `Integer` | `_compute_num_students` |
| students | student_ids | `One2many('sp_olympiad.student','project_id')` | |
| — | event_id | `Many2one('sp_olympiad.event')` | required |
| — | state | `Selection` | draft/submitted/paid/evaluated/published |
| — | project_score | `Float` | `_compute_score` (average of jury totals) |
| — | medal | `Selection` | `_compute_medal` |
| — | age_group | `Selection` | `_compute_age_group`: **max(student.age)** determines group |

**Computed logic:**  
`_compute_code` → `{event.code_prefix}{event.year}-{category.code}-{seq:03d}`  
`_compute_total` → `event.registration_fee + (num_students × nights × event.accommodation_fee) + (excursion × num_students × event.excursion_fee)`  
`_compute_medal` → uses `event.medal_gold_min`, `event.medal_silver_min`, `event.medal_bronze_min`, `event.medal_hm_min`  
`_compute_age_group` → `max(student_ids.mapped('age'))` compared against `event.age_junior_min/max`, `event.age_senior_min/max`

**Mixins:** `mail.thread`, `mail.activity.mixin` → chatter + activity tracking on project

---

## `sp_olympiad.student`

| prompt.md | Odoo Field | Type | Notes |
|-----------|------------|------|-------|
| firstName | first_name | `Char` | required |
| lastName | last_name | `Char` | required |
| — | name | `Char` | `_compute_name` = first + last |
| birthDate | birth_date | `Date` | required |
| — | age | `Integer` | `_compute_age` (relative to event date) |
| gender | gender | `Selection` | [('M','Male'),('F','Female'),('D','Diverse')] |
| country | country_id | `Many2one('res.country')` | |
| visa | visa_required | `Boolean` | |
| tshirt | tshirt_size | `Selection` | XS/S/M/L/XL/XXL |
| accommodation | accommodation_ids | `Many2many('sp_olympiad.event.accommodation')` | Selected from event's accommodation |
| noAccom | no_accommodation | `Boolean` | If True, accommodation_ids is ignored |
| — | accommodation_nights | `Integer` | `_compute_nights` = len(accommodation_ids) |
| — | project_id | `Many2one('sp_olympiad.project')` | required, ondelete=cascade |

> Available nights in the wizard are filtered by `project_id.event_id.accommodation_ids` — only nights belonging to that event are shown.

---

## `sp_olympiad.jury.member`

| prompt.md | Odoo Field | Type | Notes |
|-----------|------------|------|-------|
| id | id | Auto | |
| title | title | `Selection` | Dr. / Prof. / Mr. / Ms. / — |
| firstName + lastName | partner_id | `Many2one('res.partner')` | name from partner |
| — | user_id | `Many2one('res.users')` | Odoo login |
| email | email | `Char` | related: partner_id.email |
| password | — | `res.users` | Managed by Odoo |
| categories | category_ids | `Many2many('sp_olympiad.category')` | |
| lang | jury_lang | `Selection` | [('en','English'),('de','German'),('both','Both')] |
| assignedProjects | project_ids | `Many2many('sp_olympiad.project')` | assigned by admin |

---

## New Model: `sp_olympiad.criterion`
*(scoring criteria per category)*

| Field | Type | Notes |
|-------|------|-------|
| name | `Char` | e.g. "Innovation" |
| category_id | `Many2one('sp_olympiad.category')` | |
| max_score | `Integer` | |
| weight | `Float` | weights per category must sum to 1.0 |
| sequence | `Integer` | display order |
| apply_age_group | `Selection` | all / junior_only / senior_only |
| is_reference | `Boolean` | True = "Quelle/References" — shown but not scored for Junior (weight=0) |
| excluded_category_ids | `Many2many('sp_olympiad.category')` | Categories where this criterion is hidden (e.g. ADD) |

**Constraint:** `@api.constrains('weight', 'category_id')` → SUM(weight) for category must == 1.0

---

## `sp_olympiad.jury.score`

| prompt.md | Odoo Field | Type | Notes |
|-----------|------------|------|-------|
| projectId | project_id | `Many2one('sp_olympiad.project')` | required |
| juryEmail | jury_id | `Many2one('sp_olympiad.jury.member')` | required |
| criterionIndex | criterion_id | `Many2one('sp_olympiad.criterion')` | |
| score | score | `Float` | 0 – criterion.max_score |
| — | weighted_score | `Float` | `_compute_weighted` = score × criterion.weight |

**Mixins:** `mail.thread` → log score changes for audit trail

---

## `sp_olympiad.stand.vote`

| prompt.md | Odoo Field | Type | Notes |
|-----------|------------|------|-------|
| projectId | project_id | `Many2one('sp_olympiad.project')` | required |
| score (0–10) | score | `Integer` | 0 – event.best_stand_max_score |
| — | ip_address | `Char(45)` | IPv4/IPv6 |
| — | fingerprint | `Char(64)` | SHA-256(userAgent + screenRes + timezone + language) |
| — | vote_date | `Datetime` | auto: now() |

**Constraint:** `models.Constraint` — `UNIQUE(project_id, ip_address)` — one vote per project per IP (not global)

**Fingerprint algorithm (JS):** `SHA-256(navigator.userAgent + screen.width×height + Intl.timezone + navigator.language)`

---

## System Settings: `res.config.settings`
*(system-wide configuration — `sp_olympiad_core`)*

| Field | Type | Notes |
|-------|------|-------|
| verify_base_url | `Char` | QR base URL, e.g. `https://innovategermany.org/verify/` |
| sp_olympiad_logo | `Binary` | Default logo for certificates/letters (can be overridden per event) |

---

## Email Templates (`mail.template`)
*(defined in `sp_olympiad_mentor` and `sp_olympiad_admin`)*

| Template | Trigger | Recipient |
|----------|---------|-----------|
| Registration Confirmation | Project submitted | Mentor |
| Payment Confirmation | Stripe `payment.transaction` state='done' | Mentor |
| Research Paper Reminder | 7 days before deadline (`ir.cron`) | Mentor |
| Jury Assignment | Project assigned to jury | Jury member |
| Results Published | Admin clicks Publish | All mentors of event |
| Certificate Ready | Results published | Mentor (if medal ≥ Participation) |

---

## Python Constraints & Validations

| # | Model | Constraint | Type | Details |
|---|-------|------------|------|---------|
| C1 | `sp_olympiad.event` | `date_end >= date_start` | `@api.constrains` | Event must end after it starts |
| C2 | `sp_olympiad.event.accommodation` | `date` within `[event_id.date_start, event_id.date_end]` | `@api.constrains` | Accommodation dates must fall within event date range |
| C3 | `sp_olympiad.criterion` | `SUM(weight) per category == 1.0` | `@api.constrains` | Weights for all criteria of a category must sum to 1.0 (tolerance: 4 decimal digits) |
| C4 | `sp_olympiad.project` | `len(student_ids) <= category_id.max_participants` | `@api.constrains` | Cannot exceed category participant limit |
| C5 | `sp_olympiad.project` | `category_id.is_solo → len(student_ids) == 1` | `@api.constrains` | Solo categories (ADD, CRW) require exactly 1 student |
| C6 | `sp_olympiad.student` | `age` within `[event.age_junior_min, event.age_senior_max]` | `@api.constrains` | Student age must be between 12–19 (or event-configured range) at event date |
| C7 | `sp_olympiad.project` | `abstract_file` required before `state != 'draft'` | Validation on state transition | Cannot submit without abstract |
| C8 | `sp_olympiad.jury.score` | `0 <= score <= criterion_id.max_score` | `@api.constrains` | Score must be within criterion range |
| C9 | `sp_olympiad.project` | `paid == True` required before `state == 'paid'` | Validation on state transition | Cannot mark paid without completed payment |
| C10 | `sp_olympiad.project` | `research_paper` upload only before `event.research_paper_deadline` | Validation | Reject uploads after deadline (admin override via settings) |

---

## Access Control Matrix (`ir.model.access.csv`)

| Model | Mentor (`group_sp_olympiad_user`) | Jury (`group_sp_olympiad_jury`) | Admin (`group_sp_olympiad_admin`) | Public (no group) |
|-------|------------------------|--------------------|----------------------|-----------------|
| `sp_olympiad.event` | read | read | create, write, read, unlink | read (published only) |
| `sp_olympiad.event.accommodation` | read | read | create, write, read, unlink | read |
| `sp_olympiad.category` | read | read | create, write, read, unlink | read |
| `sp_olympiad.project` | **own**: create, write, read, unlink | read | create, write, read, unlink | read (state='published' only) |
| `sp_olympiad.student` | **own**: create, write, read, unlink | read | create, write, read, unlink | — |
| `sp_olympiad.jury.member` | — | **own**: read | create, write, read, unlink | — |
| `sp_olympiad.criterion` | read | read | create, write, read, unlink | read |
| `sp_olympiad.jury.score` | — | **own**: create, write, read, unlink | create, write, read, unlink | — |
| `sp_olympiad.stand.vote` | — | — | read | create |
| `payment.transaction` | **own**: read (portal) | — | read | — |

> **own** = record rule: `user` matches `mentor_id` (for projects) or `user_id` (for jury).  
> Public access to `sp_olympiad.project` filtered by `state='published'` via record rule.

### Record Rules

| Rule | Model | Domain | Groups |
|------|-------|--------|--------|
| Mentor sees own projects | `sp_olympiad.project` | `[('mentor_id', '=', user.id)]` | `group_sp_olympiad_user` |
| Jury sees own scores | `sp_olympiad.jury.score` | `[('jury_id.user_id', '=', user.id)]` | `group_sp_olympiad_jury` |
| Public sees published only | `sp_olympiad.project` | `[('state', '=', 'published')]` | Public (portal group, no login required) |
| Admin sees all | All models | `[]` | `group_sp_olympiad_admin` |
| Jury sees assigned projects | `sp_olympiad.project` | `[('project_ids', 'in', user.id)]` (via m2m) | `group_sp_olympiad_jury` |

---

## Model Dependency Map

```
sp_olympiad.event
    └── sp_olympiad.project ──────────── sp_olympiad_core
            ├── sp_olympiad.student       sp_olympiad_core
            ├── sp_olympiad.jury.score    sp_olympiad_jury
            └── sp_olympiad.stand.vote    sp_olympiad_vote

sp_olympiad.category
    └── sp_olympiad.criterion             sp_olympiad_jury

sp_olympiad.jury.member
    ├── sp_olympiad.jury.score            sp_olympiad_jury
    └── sp_olympiad.project (m2m)         sp_olympiad_jury

res.users / res.partner → Mentor      sp_olympiad_mentor
```

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

*This document is based on Odoo 19 development standards. All models and fields should follow the conventions documented in `.agents/skills/odoo-19/references/`.*
