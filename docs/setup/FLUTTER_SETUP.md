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

Optional: run on iOS/Android once emulators are configured.
