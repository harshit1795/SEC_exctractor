# Firestore to PostgreSQL Migration Guide

This guide explains how to migrate data from Firebase Firestore to PostgreSQL/SQLite.

## Prerequisites

1. **Firebase Credentials**: You need Firebase Admin SDK credentials
   - Option 1: Place `firebase-credentials.json` in the project root
   - Option 2: Set `FIREBASE_CREDENTIALS_JSON` environment variable with JSON string

2. **Database Setup**: Ensure your PostgreSQL/SQLite database is configured
   - Check `finq-backend/.env` for `DATABASE_URL`
   - Run migrations: `cd finq-backend && alembic upgrade head`

3. **Dependencies**: Install Firebase Admin SDK
   ```bash
   cd finq-backend
   pip install firebase-admin
   ```

## What Gets Migrated

### ✅ Migrated Data

1. **Posts** (`posts` collection → `posts` table)
   - Post content, author, timestamps
   - Post likes (from `likes` array → `post_likes` table)
   - Post comments (from `comments` array → `post_comments` table)
   - Media URLs, tags, metadata

2. **Friends** (from multiple sources)
   - Friend requests (`friend_requests` collection → `friends` table)
   - Accepted friends (from `users.friends` arrays → `friends` table)
   - Bidirectional relationships created for accepted friends

### ❌ Not Migrated (Not Relevant)

1. **User Profiles** (`users` collection)
   - User data comes from Firebase Auth, not Firestore
   - Profile data is not stored in PostgreSQL

2. **Rejected Friend Requests**
   - Rejected requests are skipped (not relevant)

3. **Other Collections**
   - Any other Firestore collections not mentioned above

## Running the Migration

### Step 1: Prepare Firebase Credentials

**Option A: Using a file**
```bash
# Place firebase-credentials.json in project root
cp /path/to/your/firebase-credentials.json .
```

**Option B: Using environment variable**
```bash
export FIREBASE_CREDENTIALS_JSON='{"type":"service_account",...}'
```

### Step 2: Run the Migration Script

```bash
cd finq-backend
python scripts/migrate_firestore.py
```

### Step 3: Verify Migration

Check the database:
```bash
# Using SQLite
sqlite3 finq.db "SELECT COUNT(*) FROM posts;"
sqlite3 finq.db "SELECT COUNT(*) FROM friends;"
sqlite3 finq.db "SELECT COUNT(*) FROM post_likes;"
sqlite3 finq.db "SELECT COUNT(*) FROM post_comments;"
```

Or use the FastAPI backend:
```bash
curl http://localhost:8000/api/nexus/posts/feed?user_id=YOUR_USER_ID
```

## Migration Details

### Data Transformations

1. **Field Name Mapping**:
   - `authorId` → `author_id`
   - `timestamp` → `created_at`
   - `userId` → `user_id`
   - `fromUserId` → `user_id`
   - `toUserId` → `friend_id`

2. **Data Structure Changes**:
   - **Likes**: Array in Firestore → Separate `post_likes` table
   - **Comments**: Array in Firestore → Separate `post_comments` table
   - **Friends**: Array in user document → Separate `friends` table

3. **Status Mapping**:
   - `pending` → `pending`
   - `accepted` → `accepted`
   - `rejected` → Skipped

### Duplicate Handling

- The script checks for existing records before inserting
- Duplicate posts, likes, comments, and friends are skipped
- Safe to run multiple times (idempotent)

### Error Handling

- Errors are logged but don't stop the migration
- Each record is processed independently
- Failed records are counted in the summary

## Troubleshooting

### Issue: "Firebase credentials not found"

**Solution**: 
- Ensure `firebase-credentials.json` exists in project root, OR
- Set `FIREBASE_CREDENTIALS_JSON` environment variable

### Issue: "Database connection error"

**Solution**:
- Check `DATABASE_URL` in `.env`
- Ensure database is running
- Run migrations: `alembic upgrade head`

### Issue: "Module not found: firebase_admin"

**Solution**:
```bash
pip install firebase-admin
```

### Issue: "Duplicate key error"

**Solution**:
- This is normal if you run the script multiple times
- The script skips existing records automatically

## Post-Migration Checklist

- [ ] Verify post counts match
- [ ] Verify friend relationships are correct
- [ ] Test feed endpoint
- [ ] Test friend requests
- [ ] Check for any data inconsistencies
- [ ] Backup the migrated database

## Rollback

If you need to rollback:
1. The original Firestore data is unchanged
2. You can drop PostgreSQL tables and re-run migration
3. Or restore from a database backup

## Support

For issues or questions:
1. Check migration logs for specific errors
2. Verify Firebase credentials are correct
3. Ensure database schema is up to date
4. Check that all dependencies are installed


