# Data Cleanup Script

## Overview
This script clears all existing user data, friends, posts, and starts fresh. Use this when you want to reset the Nexus community to a clean state.

## What Gets Deleted
- All friend relationships
- All posts
- All post likes
- All post comments
- All user profiles
- All insights

## Usage

```bash
cd finq-backend
python scripts/clear_all_data.py
```

The script will:
1. Show you a count of all existing data
2. Ask for confirmation (type "yes" to proceed)
3. Delete all data in the correct order (respecting foreign key constraints)
4. Confirm successful cleanup

## Important Notes

⚠️ **This action cannot be undone!** All user data will be permanently deleted.

After running this script:
- All existing users will need to sign in again (their profiles will be recreated automatically)
- All friendships will need to be re-established
- All posts will be deleted

## When to Use

- Starting fresh with a new userbase
- Testing the system from scratch
- After major schema changes
- When you want to reset the community

