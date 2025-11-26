# Database Architecture: Streamlit vs Next.js Migration

## 🔄 Major Change: Firestore → PostgreSQL/SQLite

The database architecture has **changed significantly** during the migration from Streamlit to Next.js/FastAPI.

---

## 📊 Streamlit Version (Original)

### Database: **Firebase Firestore** (NoSQL)

**Collections Used:**
1. **`users`** - User profiles
   - Document ID: `user_id`
   - Fields: `displayName`, `email`, `friends` (array), `profilePictureUrl`, etc.

2. **`posts`** - Social posts
   - Document ID: Auto-generated
   - Fields: `authorId`, `content`, `timestamp`, `likes` (array), `comments` (array)

3. **`friend_requests`** - Friend requests
   - Document ID: Auto-generated
   - Fields: `fromUserId`, `toUserId`, `status` ('pending', 'accepted', 'rejected')

**Location:** `components/nexus_firebase.py`

**Characteristics:**
- NoSQL document database
- Denormalized data (friends stored as arrays in user documents)
- Real-time updates via Firestore listeners
- Serverless, managed by Google

---

## 🗄️ Next.js/FastAPI Version (Current)

### Database: **PostgreSQL** (Production) / **SQLite** (Development)

**Tables Used:**
1. **`posts`** - Social posts
   ```sql
   - id (String, PK)
   - author_id (String, indexed)
   - content (Text)
   - media_urls (JSON)
   - media_type (String)
   - likes_count (Integer)
   - comments_count (Integer)
   - shares_count (Integer)
   - is_shared_insight (Boolean)
   - insight_id (String, FK to insights)
   - tags (JSON)
   - created_at (DateTime)
   - updated_at (DateTime)
   ```

2. **`post_likes`** - Post likes (separate table)
   ```sql
   - id (String, PK)
   - post_id (String, FK to posts)
   - user_id (String, indexed)
   - created_at (DateTime)
   ```

3. **`post_comments`** - Post comments (separate table)
   ```sql
   - id (String, PK)
   - post_id (String, FK to posts)
   - user_id (String, indexed)
   - content (Text)
   - created_at (DateTime)
   - updated_at (DateTime)
   ```

4. **`friends`** - Friend relationships (normalized)
   ```sql
   - id (String, PK)
   - user_id (String, indexed)
   - friend_id (String, indexed)
   - status (String: 'pending', 'accepted', 'blocked')
   - created_at (DateTime)
   - updated_at (DateTime)
   ```

5. **`insights`** - AI-generated insights
   ```sql
   - id (String, PK)
   - user_id (String, indexed)
   - chat_session_id (String)
   - prompt (Text)
   - response (Text)
   - context_data (JSON)
   - created_at (DateTime)
   ```

**Location:** 
- Models: `finq-backend/app/models/`
- Database config: `finq-backend/app/database.py`
- Migrations: `finq-backend/alembic/versions/`

**Characteristics:**
- Relational SQL database
- Normalized data (separate tables for likes, comments, friends)
- ACID transactions
- Better for complex queries and relationships
- Uses SQLAlchemy ORM

---

## 🔑 Key Differences

| Aspect | Streamlit (Firestore) | Next.js (PostgreSQL/SQLite) |
|--------|----------------------|----------------------------|
| **Database Type** | NoSQL Document Store | Relational SQL Database |
| **Data Structure** | Denormalized (nested) | Normalized (separate tables) |
| **Friends Storage** | Array in user document | Separate `friends` table |
| **Likes Storage** | Array in post document | Separate `post_likes` table |
| **Comments Storage** | Array in post document | Separate `post_comments` table |
| **Queries** | Firestore queries | SQL queries via SQLAlchemy |
| **Real-time** | Built-in Firestore listeners | WebSocket (custom implementation) |
| **Scalability** | Auto-scaling (serverless) | Manual scaling required |
| **Cost** | Pay-per-use | Fixed hosting cost |

---

## ⚠️ Important Notes

### 1. **Data Migration Required**
The databases are **completely separate**. Existing Firestore data is **NOT automatically migrated**. If you want to migrate existing data:

- **Option A**: Keep both databases running (dual-write period)
- **Option B**: Write a migration script to copy data from Firestore to PostgreSQL
- **Option C**: Start fresh with the new database (current approach)

### 2. **User Authentication**
- **Streamlit**: Firebase Auth + Firestore
- **Next.js**: Firebase Auth (same) + PostgreSQL (different storage)

User authentication still uses Firebase, but user data storage has changed.

### 3. **Real-time Updates**
- **Streamlit**: Firestore real-time listeners
- **Next.js**: WebSocket implementation (`finq-backend/app/api/websocket.py`)

---

## 📝 Migration Path (If Needed)

If you want to migrate existing Firestore data to PostgreSQL:

1. **Create migration script** (`finq-backend/scripts/migrate_firestore.py`):
   ```python
   # Read from Firestore
   # Transform data structure
   # Write to PostgreSQL via SQLAlchemy
   ```

2. **Data mapping:**
   - `users` collection → Not directly migrated (user data comes from Firebase Auth)
   - `posts` collection → `posts` table
   - `friend_requests` collection → `friends` table
   - Likes/comments arrays → `post_likes` and `post_comments` tables

3. **Run migration:**
   ```bash
   python finq-backend/scripts/migrate_firestore.py
   ```

---

## 🎯 Current Status

**Current Implementation:**
- ✅ New database architecture fully implemented
- ✅ All Nexus features working with PostgreSQL/SQLite
- ✅ WebSocket for real-time updates
- ⚠️ **No automatic data migration from Firestore**

**Recommendation:**
- If you have existing Firestore data you want to keep, we should create a migration script
- If starting fresh, the current implementation is ready to use

---

## 📚 Related Files

**Streamlit (Old):**
- `components/nexus_firebase.py` - Firestore operations
- `pages/nexus_tabs/*.py` - UI components using Firestore

**Next.js (New):**
- `finq-backend/app/models/` - SQLAlchemy models
- `finq-backend/app/api/nexus.py` - API endpoints using PostgreSQL
- `finq-backend/app/database.py` - Database configuration
- `finq-backend/alembic/` - Database migrations

---

**Summary**: The architecture has migrated from **Firebase Firestore (NoSQL)** to **PostgreSQL/SQLite (SQL)** for better structure, relationships, and query capabilities. This is a significant architectural improvement but requires data migration if you want to preserve existing Firestore data.

