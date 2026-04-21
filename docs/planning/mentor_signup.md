# Mentor Signup Implementation Plan

## Goal
Create a mentor registration system that:
1. Has its own signup form at `/mentor/signup`
2. Automatically adds users to `group_sp_olympiad_mentor`
3. Requires email verification via link
4. Supports country selection
5. Allows admin to deactivate mentors

---

## 1. New Model: `sp_olympiad.mentor`

**File:** `models/olympiad_mentor.py`

### Fields
| Field | Type | Description |
|-------|------|-------------|
| user_id | many2one(res.users) |关联 Odoo user |
| name | char (related) | Display name |
| email | char (related) | Email address |
| country_id | many2one(res.country) | Country selection |
| branch | char | Field/Subject (e.g. Physics, Math) |
| phone | char | Contact phone |
| verified | boolean | Email verified? |
| active | boolean | Admin active toggle |

### Constraints
- `user_id` must be unique (one user = one mentor)
- Email format validation

---

## 2. Settings Extension

**File:** `models/res_config_settings.py`

### New Fields
| Field | Type | Description |
|-------|------|-------------|
| mentor_signup_enabled | boolean | Allow mentor signup |
| mentor_email_template_id | many2one(mail.template) | Email template for verification |

### UI
Add to `Olympiad > Configuration > General Settings`:
- [x] Enable Mentor Signup
- Email Template selector

---

## 3. Email Verification

### Token Generation
- On mentor signup, generate unique token
- Store in `sp_olympiad.mentor.verification_token`
- Token expires in 24 hours

### Email Template
```html
<!-- /views/mentor_email_template.xml -->
<p>Dear <t t-out="mentor.name">,</p>
<p>Please click the link below to verify your mentor account:</p>
<a t-attf-href="/mentor/verify/#{mentor.verification_token}">Verify your email</a>
```

### Verification Flow
```
POST /mentor/signup
    ↓
Generate token, send email
    ↓
User clicks link → /mentor/verify/TOKEN
    ↓
Controller validates token
    ↓
Set verified=True
    ↓
Redirect to login
```

---

## 4. Signup Controller

**File:** `controllers/mentor_signup.py`

### Routes
| Route | Method | Description |
|-------|--------|-------------|
| `/mentor/signup` | GET | Render signup form |
| `/mentor/submit` | POST | Process registration |
| `/mentor/verify/<token>` | GET | Verify email via link |

### Validation
- Email must be unique
- Password strength (minimum length)
- Required fields check

---

## 5. Views & Templates

### Templates
- `mentor_signup_page` - Signup form template
- `mentor_verify_page` - Verification result page
- `mentor_profile_page` - Mentor dashboard (future)

### Views
- `sp_olympiad.mentor.view.form` - Admin edit form
- `sp_olympiad.mentor.view.list` - Mentor list

### Menus
Add to `Olympiad > Configuration`:
- `Mentors` - List all mentors
- `Pending Mentors` - Filter verified=False (or remove if auto-verified)

---

## 6. Security

**File:** `security/mentor_security.xml`

### ACL
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_sp_olympiad_mentor_user,Olympiad Mentor user,model_sp_olympiad_mentor,group_sp_olympiad_admin,1,1,1,1
access_sp_olympiad_mentor_public,Olympiad Mentor public,model_sp_olympiad_mentor,base.group_public,1,0,0,0
```

---

## 7. Menu Controls

**File:** `views/menu_views.xml`

Add conditional menu items based on settings:
```xml
<menuitem id="menu_olympiad_mentors"
          name="Mentors"
          parent="menu_olympiad_config"
          action="action_olympiad_mentor_list"
          sequence="30"
          groups="group_sp_olympiad_admin"/>
```

---

## 8. Migration Steps

1. Add `sp_olympiad.mentor` model
2. Add settings fields
3. Create email template
4. Create controller and routes
5. Create views/templates
6. Update security
7. Update documentation

---

## Flow Diagram

```
User visits /mentor/signup
    ↓
Fills form (email, password, name, country, branch, phone)
    ↓
POST /mentor/submit
    ↓
1. Create res.users (base.group_user)
2. Add to group_sp_olympiad_mentor
3. Create sp_olympiad.mentor (verified=False)
4. Generate verification_token
5. Send email with verification link
    ↓
User clicks /mentor/verify/TOKEN
    ↓
Controller validates token (not expired, exists)
    ↓
Set verified=True
    ↓
Redirect to /web/login
    ↓
User can login with mentor access
```

---

## Future Enhancements

1. Mentor dashboard (project list, students)
2. Profile edit form
3. Deactivate email notification
4. Mentor invitation workflow (admin sends invite)

---

## Decision Log

### 2026-04-21 - Mentor Registration Approach

**Decision:** Use Odoo's built-in `res.users` model with custom `sp_olympiad.mentor` profile, email-based verification only (no admin approval required).

**Context:** 
- Admin wants to be able to assign users to multiple roles (Staff + Jury, etc.)
- Mentor should be able to self-register
- Simple workflow: signup → email verify → access granted

**Rationale:**
- No admin approval step needed (simplifies workflow)
- Email verification sufficient for initial validation
- Admin can still deactivate mentors from the list view
- Future: Payment-based project submission and approval will add another layer

**Changes:**
- `sp_olympiad.mentor.verified` = True after email verification (auto, no admin action)
- Admin menu for mentor management: list, deactivate (set active=False)
- No `action_activate()` needed - mentors auto-activate after email verify
