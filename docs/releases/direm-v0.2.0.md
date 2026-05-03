# DIREM v0.2.0 - Bunker and UX Polish

Release date: 2026-05-03

## Summary

DIREM v0.2.0 builds on the Core MVP with a more usable Telegram experience, Bunker Mode, expanded timezone selection, home status stats, and release-ready docs. Reminder delivery remains a basic worker MVP, now with user-level Bunker suppression and safe rescheduling when Bunker is turned off.

## Added

- Lightweight localized first-run onboarding after `/start`.
- Expanded `/timezone` picker with Kazakhstan shortcuts, curated region lists for Kazakhstan, Russia, Europe, Asia, America and UTC / GMT, plus manual IANA input.
- Localized Telegram main menu and List, Settings and Help hubs.
- Bunker Mode design and accepted ADR.
- User-level Bunker persistence fields and service foundation.
- Worker suppression for reminders owned by users with active Bunker state.
- Telegram `/bunker` UX and direct Bunker ON/OFF reply-keyboard toggle.
- Atomic Bunker deactivation rescheduling for active reminders to avoid catch-up delivery.
- Home status reminder stats for the current Telegram user.
- Main menu navigation on final/action-result messages.
- README hero image under `docs/assets/direm-readme-hero.png`.

## Changed

- Removed stale `Dorpheus` references from DIREM examples and tests.
- Refined README and runtime smoke docs for the current v0.2.0 behavior.

## Known Limitations

- No timed Bunker.
- No per-reminder snooze.
- No Bunker history.
- No delivery history command.
- No retry scheduler.
- No reminder editing.
- No dashboard or webhook mode.
- No AI or web UI.
- Worker delivery remains a basic MVP, not production-grade observability or retry infrastructure.
- User-authored reminder title and message text are not auto-translated.

## Checks

- `python -m pytest` -> 176 passed.
- `python -m compileall src alembic tests` -> passed.
- `docker compose config` -> passed.
- `docker compose run --rm bot alembic heads` -> `20260503_004_bunker_state (head)`.
- `docker compose run --rm bot alembic current` -> `20260503_004_bunker_state (head)`.
- `docker compose run --rm bot alembic upgrade head` -> passed.
- `docker compose run --rm bot alembic current` -> `20260503_004_bunker_state (head)`.

## Credits

- Project direction: 1D1L1R
- Architecture, scope lock and review: Rein Hard V
- Implementation and release execution: Bushid Ronin V

Credits preserved:
1D1L1R · Rein Hard V · Bushid Ronin V
