# ✅ Vercel Environment Variable Format

## Answer: NO Quotes Needed!

In Vercel's Environment Variables UI, **do NOT use quotes** around the values.

---

## ✅ Correct Format

When adding environment variables in Vercel:

**Key**: `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID`  
**Value**: `123456789012` ← **No quotes!**

**Key**: `NEXT_PUBLIC_FIREBASE_API_KEY`  
**Value**: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX` ← **No quotes!**

**Key**: `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`  
**Value**: `your-project.firebaseapp.com` ← **No quotes!**

---

## ❌ Wrong Format (Don't Do This)

**Key**: `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID`  
**Value**: `"123456789012"` ← **Don't include quotes!**

**Key**: `NEXT_PUBLIC_FIREBASE_API_KEY`  
**Value**: `"AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"` ← **Don't include quotes!**

---

## 📋 Examples

### Firebase Config Values (No Quotes)

```
NEXT_PUBLIC_FIREBASE_API_KEY = AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN = your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID = your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET = your-project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID = 123456789012
NEXT_PUBLIC_FIREBASE_APP_ID = 1:123456789012:web:abcdef123456
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID = G-XXXXXXXXXX
NEXT_PUBLIC_API_URL = https://secexctractor-production.up.railway.app/api
```

**Just paste the values directly, no quotes needed!**

---

## 🔍 Why No Quotes?

- Vercel's UI handles the values as strings automatically
- Adding quotes would make the value include the quotes (e.g., `"123456789012"` instead of `123456789012`)
- Next.js reads these as strings anyway via `process.env.NEXT_PUBLIC_*`

---

## ✅ Quick Guide

1. **Key field**: Type the variable name (e.g., `NEXT_PUBLIC_FIREBASE_API_KEY`)
2. **Value field**: Paste the value **without quotes** (e.g., `AIzaSy...`)
3. **Save**

That's it! No quotes needed. 🚀

