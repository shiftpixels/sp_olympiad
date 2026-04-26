# Migration Notes

This document tracks schema changes that require special attention during module upgrades.

## Schema Changes History

### 2026-04-25 - Mentor Model Schema Changes

#### 1. Added WhatsApp Field
- **Change**: Added `whatsapp` field to `sp_olympiad.mentor` model
- **Type**: New field addition
- **Impact**: Non-breaking change
- **Migration**: Automatic (Odoo handles new field additions)
- **Notes**: 
  - Field is optional (no required=True)
  - No data migration needed
  - Existing records will have empty values

#### 2. Made country_id Required
- **Change**: Added `required=True` to `country_id` field in `sp_olympiad.mentor` model
- **Type**: Field constraint change
- **Impact**: Potential breaking change for existing records
- **Migration**: Manual data cleanup may be required
- **Notes**:
  - Existing mentor records without country_id will fail validation
  - Admin should review and update existing records before upgrade
  - Recommended query to find affected records:
    ```sql
    SELECT id, name, email FROM sp_olympiad_mentor WHERE country_id IS NULL;
    ```

#### 3. Removed Redundant Fields
- **Change**: Removed `active` and `user_active` fields from `sp_olympiad.mentor` model
- **Type**: Field removal
- **Impact**: Non-breaking change
- **Migration**: Automatic (Odoo handles field removal)
- **Notes**:
  - These fields were redundant with `res.users.active`
  - No data loss (functionality moved to user model)
  - Existing data not affected

## Upgrade Instructions

### Before Upgrade
1. **Backup Database**: Always create a full database backup before upgrading
2. **Check for Null country_id**: Run the following query to identify mentors without country:
   ```sql
   SELECT id, name, email FROM sp_olympiad_mentor WHERE country_id IS NULL;
   ```
3. **Update Null country_id Records**: If any records found, update them with valid country IDs:
   ```sql
   UPDATE sp_olympiad_mentor SET country_id = (SELECT id FROM res_country WHERE code = 'TR' LIMIT 1) WHERE country_id IS NULL;
   ```

### During Upgrade
1. **Install Module**: Use standard Odoo upgrade process
2. **Monitor Logs**: Check for any constraint violations during upgrade
3. **Verify Data**: After upgrade, verify that all mentor records have valid country_id

### After Upgrade
1. **Test Functionality**: Verify mentor signup and verification still work
2. **Check Access Rights**: Ensure mentors can still access their profiles
3. **Review Settings**: Verify Olympiad settings are intact

## Rollback Plan

If issues occur after upgrade:

1. **Restore Database**: Restore from pre-upgrade backup
2. **Revert Code**: Revert to previous module version
3. **Investigate Issue**: Analyze logs to identify root cause
4. **Fix and Retry**: Apply fix and attempt upgrade again

## Data Validation Queries

### Verify Mentor Records
```sql
-- Check total mentor count
SELECT COUNT(*) FROM sp_olympiad_mentor;

-- Check mentors with country_id
SELECT COUNT(*) FROM sp_olympiad_mentor WHERE country_id IS NOT NULL;

-- Check mentors without country_id (should be 0 after upgrade)
SELECT COUNT(*) FROM sp_olympiad_mentor WHERE country_id IS NULL;

-- Check mentors with whatsapp field
SELECT COUNT(*) FROM sp_olympiad_mentor WHERE whatsapp IS NOT NULL AND whatsapp != '';
```

### Verify User Records
```sql
-- Check mentor users
SELECT u.id, u.login, u.active, m.verified 
FROM res_users u 
JOIN sp_olympiad_mentor m ON u.id = m.user_id;

-- Check for orphaned mentor records (no user)
SELECT id, name, email FROM sp_olympiad_mentor WHERE user_id IS NULL;
```

## Known Issues and Limitations

### Current Limitations
- No automated migration scripts for data cleanup
- Manual intervention required for records with null country_id
- No rollback mechanism for field removal

### Future Improvements
- Add pre-upgrade validation scripts
- Implement automated data migration
- Add post-upgrade verification checks
- Create rollback procedures

## Contact Information

For questions or issues related to migrations:
- Review this document first
- Check Odoo logs for error messages
- Contact development team if issues persist
