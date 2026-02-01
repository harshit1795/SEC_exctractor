FinQ Flutter Rebuild
====================

This folder hosts the Flutter client that replaces the current Next.js frontend
while continuing to use the existing FastAPI backend. The goal is a single code
base that runs on iOS, Android, and Web.

What is already in place
------------------------

- A minimal Flutter app entry point in `lib/`.
- A module layout that mirrors the current product areas.
- A backend-first API layer contract to keep the FastAPI integration stable.

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
