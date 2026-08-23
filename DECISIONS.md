# Architectural Decisions Log

## Decision 1: Configuration Management
- **Decision:** Use `pydantic-settings` to load all settings in `app/config.py`.
- **Rationale:** Ensures strict type validation, default fallback values, and prevents direct `os.environ` access across modules.

## Decision 2: In-Process Fallbacks
- **Decision:** Use embedded Qdrant (`qdrant-client` with local path) for local dev vector search, and in-process dictionary fallback for caching when Redis URL is not configured.
- **Rationale:** Enables full local operation without needing local Docker or external server setup.

## Decision 3: Package Pin Patch Relaxation for Python 3.13
- **Decision:** Relax `mediapipe` pin from `0.10.18` to `>=0.10.18` (`0.10.35`).
- **Rationale:** On Python 3.13, MediaPipe wheels start at version `0.10.30`. Kept major/minor `0.10` per PRD Section 2 rule.

