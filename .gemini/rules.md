# FINQ Project System Prompt & Global Standards

This document establishes the architecture, code guidelines, and automated workflow constraints for the FINQ Financial Analysis Platform. All AI interactions and code generated within this repository must adhere to these rules.

## 1. Project Architecture
The platform is composed of three primary modules:
- `finq-backend/`: The Python FastAPI backend utilizing SQLite (`finq.db`) and Alembic for database migrations. Port `8000`.
- `finq-flutter/`: The unified Dart/Flutter codebase for Android, iOS, and Web. Requires Firebase and specific `.dart-define.json` configurations.
- `finq-frontend/`: A legacy Next.js web application (largely superseded by the Flutter Web client, but still maintained).

## 2. Core Operational Rules
- **Base Branch Rule**: ALL future development MUST branch solely from `flutter-rebuild`. Do not branch from or commit directly to `main` without explicit human direction.
- **No-Merge Policy**: Agents are strictly forbidden from executing destructive actions. UNDER NO CIRCUMSTANCE should an agent execute `git merge` or `gh pr merge`. Only human reviewers possess merge authorization.
- **No Silent Failures**: Any changes must handle exceptions gracefully (e.g., using `try/catch` in Dart, explicit `HTTPException` catches in FastAPI).
- **Test Before Concluding**: Always execute tests specific to the module you modified.
  - *Backend*: Run `pytest` from the `finq-backend` dir.
  - *Flutter*: Run `flutter test` from the `finq-flutter` dir.
- **Database Modularity**: If modifying models in `finq-backend/app/models/`, you MUST generate a new Alembic migration using `alembic revision --autogenerate -m "message"`. Do not alter the `.db` file directly without migrations.

## 3. Technology & Syntax Standards
### Flutter / Dart (`finq-flutter`)
- Use Riverpod (`flutter_riverpod`) for State Management. No Provider or GetX.
- WebSockets (`web_socket_channel`) logic should be decoupled into Repository patterns.
- Follow strict typing; use `?` for nullable types explicitly. Avoid `dynamic` wherever possible.
- Use `GoRouter` for navigation.

### Backend (`finq-backend`)
- Use `Pydantic v2` schemas strictly for request/response models.
- Dependency injection should be handled via `UploadFile` and `Depends`.
- Async functions for I/O operations (DB queries via SQLAlchemy async API, external API calls via `httpx`).
- Stick strictly to PEP 8 standards and format code with standard Python formatters (e.g. `black`, `ruff`).

## 4. End-to-End Workflow Awareness
Whenever you are fulfilling an objective that touches both clients and APIs:
1. Identify the contract change in the FastAPI endpoints (`app/api/` and `app/schemas/`).
2. Update the Dart equivalent model in `finq-flutter/lib/features/*/models`.
3. Verify changes through unit/integration tests before finalizing.

## 5. Overnight Worker Constraint
When acting as an autonomous worker on generic task tracking artifacts (e.g. `overnight.md` workflows), ensure that:
1. Errors during CI script runs lead to immediate diagnostic fixes.
2. The agent limits scope strictly to predefined milestones. No architecture rewrites unless defined in the task document.
