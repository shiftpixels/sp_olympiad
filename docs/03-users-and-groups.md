# Users and Groups

This document describes the user access control system for the `sp_olympiad` module.

## Olympiad User Groups

### Group Hierarchy

| Sequence | Group | Description | Access Level |
|----------|-------|-------------|--------------|
| 10 | Olympiad Admin | Full access to all features and settings | Full CRUD + Settings |
| 20 | Olympiad Staff | Operational access to events and categories | Full CRUD (no settings) |
| 30 | Olympiad Mentor | Create and manage own projects/students only | Limited CRUD |
| 40 | Olympiad Jury | View assigned projects and submit scores | Read + Scoring |

### Menu Access by Group

| Menu | Admin | Staff | Mentor | Jury |
|------|-------|-------|--------|------|
| Olympiad (root) | ✓ | ✓ | ✓ | ✓ |
| Events | ✓ | ✓ | ✓ | ✓ |
| Configuration | ✓ | ✓ | ✗ | ✗ |
| Categories | ✓ | ✓ | ✗ | ✗ |
| General Settings | ✓ | ✗ | ✗ | ✗ |

## Group Details

| Group | XML ID | Inherits | Includes |
|-------|--------|----------|----------|
| Olympiad Admin | `group_sp_olympiad_admin` | `base.group_user` | `base.user_root`, `base.user_admin` |
| Olympiad Staff | `group_sp_olympiad_staff` | `base.group_user` | - |
| Olympiad Mentor | `group_sp_olympiad_mentor` | `base.group_user` | - |
| Olympiad Jury | `group_sp_olympiad_jury` | `base.group_user` | - |

## Current Menu Configuration

**File:** `addons_dev/sp_olympiad/views/menu_views.xml`

```xml
<!-- Olympiad root - visible to all logged-in users -->
<menuitem id="menu_olympiad_root"
          name="Olympiad"
          sequence="10"
          groups="group_sp_olympiad_admin,group_sp_olympiad_staff,group_sp_olympiad_mentor,group_sp_olympiad_jury"/>

<!-- Events Menu - visible to Admin, Staff, Mentor, Jury -->
<menuitem id="menu_olympiad_events"
          name="Events"
          parent="menu_olympiad_root"
          action="action_olympiad_event"
          sequence="10"
          groups="group_sp_olympiad_admin,group_sp_olympiad_staff,group_sp_olympiad_mentor,group_sp_olympiad_jury"/>

<!-- Configuration Menu - visible to Admin, Staff only -->
<menuitem id="menu_olympiad_config"
          name="Configuration"
          parent="menu_olympiad_root"
          sequence="100"
          groups="group_sp_olympiad_admin,group_sp_olympiad_staff"/>

<menuitem id="menu_olympiad_category"
          name="Categories"
          parent="menu_olympiad_config"
          action="action_olympiad_category"
          sequence="10"
          groups="group_sp_olympiad_admin,group_sp_olympiad_staff"/>

<menuitem id="menu_olympiad_settings"
          name="General Settings"
          parent="menu_olympiad_config"
          action="action_sp_olympiad_config_settings"
          sequence="20"
          groups="group_sp_olympiad_admin"/>
```

## Security Implementation

**File:** `addons_dev/sp_olympiad/security/sp_olympiad_security.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Security category -->
    <record id="sp_olympiad_security_category" model="ir.module.category">
        <field name="name">Olympiad</field>
        <field name="description">Olympiad Management Access Rights</field>
        <field name="sequence">10</field>
    </record>

    <!-- Privilege record (Odoo 19+) -->
    <record id="privilege_sp_olympiad" model="res.groups.privilege">
        <field name="name">Olympiad Privilege</field>
        <field name="category_id" ref="sp_olympiad_security_category"/>
    </record>

    <!-- Group: Olympiad Admin - Full Access -->
    <record id="group_sp_olympiad_admin" model="res.groups">
        <field name="name">Olympiad Admin</field>
        <field name="privilege_id" ref="privilege_sp_olympiad"/>
        <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
        <field name="user_ids" eval="[(4, ref('base.user_root')), (4, ref('base.user_admin'))]"/>
        <field name="comment">Full access to all Olympiad features and settings.</field>
        <field name="sequence">10</field>
    </record>

    <!-- Group: Olympiad Staff - Operational Access -->
    <record id="group_sp_olympiad_staff" model="res.groups">
        <field name="name">Olympiad Staff</field>
        <field name="privilege_id" ref="privilege_sp_olympiad"/>
        <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
        <field name="comment">Operational access to Olympiad events and projects.</field>
        <field name="sequence">20</field>
    </record>

    <!-- Group: Olympiad Mentor - Own Projects Only -->
    <record id="group_sp_olympiad_mentor" model="res.groups">
        <field name="name">Olympiad Mentor</field>
        <field name="privilege_id" ref="privilege_sp_olympiad"/>
        <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
        <field name="comment">Access to create and manage own projects and students only.</field>
        <field name="sequence">30</field>
    </record>

    <!-- Group: Olympiad Jury - Assigned Projects and Scoring -->
    <record id="group_sp_olympiad_jury" model="res.groups">
        <field name="name">Olympiad Jury</field>
        <field name="privilege_id" ref="privilege_sp_olympiad"/>
        <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
        <field name="comment">Access to view assigned projects and submit scores only.</field>
        <field name="sequence">40</field>
    </record>
</odoo>
```

## Future Enhancements

### Planned Group Capabilities

| Group | Events | Categories | Projects | Students | Scoring | Settings |
|-------|--------|------------|----------|----------|---------|----------|
| Admin | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Staff | ✓ | ✓ | ✓ | ✓ | - | - |
| Mentor | - | - | ✓ | ✓ | - | - |
| Jury | - | - | - | - | ✓ | - |

### Next Steps

1. Create `sp_olympiad.project` model with mentor ownership
2. Create `sp_olympiad.student` model linked to projects
3. Implement jury assignment and scoring workflows
4. Add menu items and views for each group's capabilities
