FinQ Flutter - Cross-Platform Financial Analytics
==================================================

🎉 **Status**: Feature-complete and production-ready for Web!

This folder contains the Flutter client that replaces the Next.js frontend while
using the existing FastAPI backend. A single codebase runs on iOS, Android, and Web.

✅ What's Implemented
---------------------

### All Major Features (100%)
- ✅ **Dashboard** - 8 tabs with comprehensive financial analysis
- ✅ **Nexus Community** - Social features with 4 tabs
- ✅ **Financial Health** - Health monitoring with 2 tabs
- ✅ **Settings** - User preferences and app info
- ✅ **Authentication** - Email/Password + Google Sign-in
- ✅ **Real-time** - WebSocket integration for live updates
- ✅ **AI Chat** - Gemini-powered financial insights

Recommended Flutter packages (add via `flutter pub add`)
--------------------------------------------------------

- `dio` for HTTP
- `web_socket_channel` for real-time updates
- `firebase_core` and `firebase_auth` for auth
- `go_router` for navigation
- `flutter_riverpod` for state management
- `intl` for formatting

Setup notes
-----------

For a full setup walkthrough, see `docs/setup/FLUTTER_SETUP.md`.

1) Install Flutter locally and confirm `flutter --version`.
2) If platform folders are missing, run:
   `flutter create --platforms=android,ios,web .`
3) Add dependencies using `flutter pub add` (see list above).
4) Configure Firebase using FlutterFire and generate platform configs.
5) Enable Email/Password auth in Firebase Console.
6) Enable Google provider if you want Google sign-in.

Run the app
-----------

From `finq-flutter/`:

```bash
flutter pub get
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000/api
```

For web auth, pass Firebase config values:

```bash
flutter run -d chrome \
  --dart-define=API_BASE_URL=http://localhost:8000/api \
  --dart-define=FIREBASE_API_KEY=your_api_key \
  --dart-define=FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com \
  --dart-define=FIREBASE_PROJECT_ID=your_project_id \
  --dart-define=FIREBASE_STORAGE_BUCKET=your_project.appspot.com \
  --dart-define=FIREBASE_MESSAGING_SENDER_ID=your_sender_id \
  --dart-define=FIREBASE_APP_ID=your_app_id \
  --dart-define=FIREBASE_MEASUREMENT_ID=your_measurement_id
```

Local secrets (recommended)
---------------------------

Create `finq-flutter/.dart-define.json` (ignored by git) from the example:

```bash
cp .dart-define.example.json .dart-define.json
```

Then run:

```bash
flutter run -d chrome --dart-define-from-file=.dart-define.json
```

Once iOS/Android tooling is configured, you can run:

```bash
flutter run -d ios
flutter run -d android
```

Module map (from current app)
-----------------------------

- Dashboard: financial charts, chat insights, disclosures, earnings
- Nexus: social feed, friends, profiles
- Health: scores and metrics
- Settings: profile and preferences

Backend integration
-------------------

The backend is framework-agnostic. Keep the same REST endpoints and WebSocket
routes. The API contract should mirror `finq-frontend/lib/api.ts` and the FastAPI
routes in `finq-backend/app/api/`.
