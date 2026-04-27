# Changelog

## [0.1.0] - Unreleased

### Added
- Initial DIREM project skeleton.
- Docker Compose baseline with bot, worker and PostgreSQL services.
- Version and credits metadata stubs.
- Alembic baseline with a minimal `users` table migration.
- Domain schema foundation for reminders, reminder deliveries and user states.
- Domain constants for schedule types, reminder statuses and delivery statuses.
- Repository skeletons for users, reminders, deliveries and user states.
- Timezone-aware schedule calculation domain logic for interval and daily reminders.
- Active window validation and no catch-up storm scheduling behavior.
- User registration/update on `/start`.
- `/timezone` flow with IANA timezone validation and persistence.
- `/new` reminder creation flow for interval and daily reminders.
- Reminder creation service wiring with timezone-aware `next_run_at` calculation.
- `/list` reminder records flow for the current Telegram user.
- `/pause` and `/resume` reminder status flows for the current Telegram user.
- `/delete` reminder deletion flow for the current Telegram user.
- Worker delivery MVP for due active reminders.
- Delivery records for successful and failed worker send attempts.
- Runtime smoke and v0.1.0 release-readiness checklist.
- Safe `.env.example` placeholder for Telegram bot token.
- Runtime smoke fix for `/new` confirmation session injection.
- Worker startup log guard for missing schema before migrations.
- Runtime smoke fix for `/pause`, `/resume` and `/delete` selection prompt active-window rendering.
- Telegram command menu registration.
- `/cancel` command for active FSM flows.
- User-facing fallback messages for text input in `/new` button-only steps.
- Inline reminder control buttons for `/pause`, `/resume` and `/delete`.
- Inline delete confirmation while preserving manual number/id fallback.
