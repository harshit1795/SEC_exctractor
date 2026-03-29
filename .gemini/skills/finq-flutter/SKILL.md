---
name: finq-flutter
description: Development workflow for the unified Dart/Flutter codebase for FINQ across iOS, Android, and Web components.
author: SEC_extractor
version: 1.0.0
---

# 📱 FinQ Flutter Mobile & Web Engineering

**Objective**: Aid architecture scaling and feature implementations in the FINQ multi-platform Flutter app.

## Core Directives
1. **State Management**: The app uses `flutter_riverpod`. All business logic should live in standard Providers (`NotifierProvider` or `AsyncNotifierProvider`). No UI logic inside `build()` that does not rely on Riverpod `ref.watch()`.
2. **Routing Config**: Handled strictly via `go_router`. New screens require new route mappings in the main router block.
3. **Null Safety**: All models must leverage explicit Null Tracking. Use Freezed or JSON Serializable mapping to serialize backend Pydantic endpoints securely.

## Workflow Commands
### Environment Injection (`.dart-define.json`)
The client consumes API logic via `API_BASE_URL` defined in `.dart-define.json` inside the repository root. Ensure you are referencing configuration constants gracefully avoiding hard-coding keys or URLs.

### Testing Flutter Changes
Any newly built Flutter component needs widget tests. `flutter test` must pass before closing tasks.
```bash
cd finq-flutter
flutter test
```

### Static Analysis
Dart is strictly typed. Always execute `flutter analyze` internally:
```bash
cd finq-flutter
flutter clean
flutter pub get
flutter analyze
```

## Integrating Backend Data
Whenever consuming a newly drafted `/api/` endpoint:
1. Provide the JSON model class mirroring the backend's schema.
2. Build the fetch repository utilizing Riverpod.
3. Wire the repository to a localized Provider instance to cache states.
