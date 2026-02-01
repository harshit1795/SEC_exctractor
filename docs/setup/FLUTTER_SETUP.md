Flutter Setup (Phase 1)
=======================

This phase installs Flutter and initializes the cross-platform project for
iOS, Android, and Web.

1) Install Flutter (macOS)
--------------------------

Using Homebrew:

```bash
brew install --cask flutter
```

Verify:

```bash
flutter --version
```

If Homebrew is not available, follow the official install steps:
https://docs.flutter.dev/get-started/install/macos

2) Initialize platform folders
------------------------------

From the repo root:

```bash
cd finq-flutter
flutter create --platforms=android,ios,web .
```

3) Check environment
--------------------

```bash
flutter doctor
```

Resolve any warnings for:
- Xcode (iOS builds)
- Android Studio SDK (Android builds)
- Chrome (Web builds)

4) Add core dependencies
------------------------

```bash
flutter pub add dio web_socket_channel firebase_core firebase_auth go_router flutter_riverpod intl
```

5) Run the app
-------------

```bash
flutter run -d chrome
```

6) Configure Firebase (required for auth)
-----------------------------------------

Mobile (iOS/Android) uses FlutterFire:

```bash
dart pub global activate flutterfire_cli
flutterfire configure
```

Web uses `--dart-define` values:

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

In Firebase Console, enable **Authentication → Sign-in method → Email/Password**
so the login screen can authenticate.

Optional: run on iOS/Android once emulators are configured.
