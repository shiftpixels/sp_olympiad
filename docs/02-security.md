# Security

This document describes the security model and implementation for the `sp_olympiad` module.

## Security Model

### Hierarchy

```
ir.module.category (Olympiad)
    └── res.groups.privilege (Olympiad Privilege)
            ├── res.groups: group_sp_olympiad_admin (sequence: 10)
            ├── res.groups: group_sp_olympiad_staff (sequence: 20)
            ├── res.groups: group_sp_olympiad_mentor (sequence: 30)
            └── res.groups: group_sp_olympiad_jury (sequence: 40)
```

### Key Components

| Component | XML ID | Description |
|-----------|--------|-------------|
| Security Category | `sp_olympiad_security_category` | Olympiad security category |
| Privilege Record | `privilege_sp_olympiad` | Odoo 19 privilege container |
| Admin Group | `group_sp_olympiad_admin` | Full access group |
| Staff Group | `group_sp_olympiad_staff` | Operational access group |
| Mentor Group | `group_sp_olympiad_mentor` | Mentor-specific access |
| Jury Group | `group_sp_olympiad_jury` | Jury-specific access |

## Access Control

### Access Policy

1. **Authentication Required**: All module access requires `base.group_user` (internal user)
2. **Group-Based Access**: Users must be assigned to an Olympiad group
3. **Menu Visibility**: Controlled by `groups` attribute on menuitems
4. **Model Access**: Controlled by `ir.model.access.csv` records
5. **Record Rules**: Potential future addition for row-level security

### Security Design Principles

| Principle | Implementation |
|-----------|----------------|
| Least privilege | Each group has minimum required permissions |
| Separation of duties | Admin/Staff vs Mentor/Jury role separation |
| Default deny | No implicit access beyond explicitly granted permissions |
| Inheritance chain | All groups imply `base.group_user` |

## Permission Matrix

| Permission | Admin | Staff | Mentor | Jury |
|------------|-------|-------|--------|------|
| Read Events | ✓ | ✓ | ✓ | ✓ |
| Create Events | ✓ | ✓ | ✗ | ✗ |
| Edit Events | ✓ | ✓ | ✗ | ✗ |
| Delete Events | ✓ | ✓ | ✗ | ✗ |
| Read Categories | ✓ | ✓ | ✓ | ✓ |
| Create Categories | ✓ | ✓ | ✗ | ✗ |
| Edit Categories | ✓ | ✓ | ✗ | ✗ |
| Delete Categories | ✓ | ✓ | ✗ | ✗ |
| Configure Settings | ✓ | ✗ | ✗ | ✗ |
| View Projects | - | - | - | - |
| Create Projects | - | - | ✓ | - |
| Submit Scores | - | - | - | ✓ |

## File Permissions

### security/ir.model.access.csv

```
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_olympiad_event_user,Olympiad Event user,model_sp_olympiad_event,base.group_user,1,0,0,0
access_olympiad_event_manager,Olympiad Event manager,model_sp_olympiad_event,group_sp_olympiad_admin,1,1,1,1
access_olympiad_category_user,Olympiad Category user,model_sp_olympiad_category,base.group_user,1,0,0,0
access_olympiad_category_manager,Olympiad Category manager,model_sp_olympiad_category,group_sp_olympiad_admin,1,1,1,1
access_olympiad_event_accommodation_user,Olympiad Event Accommodation user,model_sp_olympiad_event_accommodation,base.group_user,1,0,0,0
access_olympiad_event_accommodation_manager,Olympiad Event Accommodation manager,model_sp_olympiad_event_accommodation,group_sp_olympiad_admin,1,1,1,1
```

### security/sp_olympiad_security.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="sp_olympiad_security_category" model="ir.module.category">
        <field name="name">Olympiad</field>
        <field name="description">Olympiad Management Access Rights</field>
        <field name="sequence">10</field>
    </record>

    <record id="privilege_sp_olympiad" model="res.groups.privilege">
        <field name="name">Olympiad Privilege</field>
        <field name="category_id" ref="sp_olympiad_security_category"/>
    </record>

    <!-- Group definitions -->
    <record id="group_sp_olympiad_admin" model="res.groups">
        <field name="name">Olympiad Admin</field>
        <field name="privilege_id" ref="privilege_sp_olympiad"/>
        <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
        <field name="user_ids" eval="[(4, ref('base.user_root')), (4, ref('base.user_admin'))]"/>
        <field name="comment">Full access to all Olympiad features and settings.</field>
        <field name="sequence">10</field>
    </record>

    <!-- Additional groups... -->
</odoo>
```

## Future Security Enhancements

### Planned Features

1. **Record Rules**: Multi-tenant isolation for mentor-owned records
2. **Access Tokens**: Public access to specific records via token
3. **Audit Logging**: Track sensitive operations
4. **API Keys**: Separate authentication for external integrations

### Security Considerations

| Area | Current | Future |
|------|---------|--------|
| Public routes | Read-only categories | Potential submission forms |
| File uploads | None | Project submissions |
| External API | None | REST API with OAuth2 |
| Webhooks | None | Event notifications |
