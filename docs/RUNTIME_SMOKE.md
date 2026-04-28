# Runtime Smoke Checklist

This checklist prepares DIREM v0.1.0 for a real Telegram runtime smoke.

## Required Automated Checks

Run these for every release-readiness pass:

```bash
python -m pytest
python -m compileall src alembic tests
docker compose config
```

## Optional Real Telegram Smoke

Run this only when the owner has configured a real local `TELEGRAM_BOT_TOKEN`.

Owner checklist:

1. Create a Telegram bot through BotFather.
2. Copy `.env.example` to `.env`.
3. Put the real bot token into local `.env`.
4. Run `docker compose up --build`.
5. Run `docker compose run --rm bot alembic upgrade head`.
6. Restart runtime services after migrations: `docker compose restart bot worker`.
7. Send `/start`.
8. Check that Telegram shows the command menu with `/language` and `/cancel`.
9. Send `/language`, choose Қазақша, then verify `/help` is in Kazakh.
10. Send `/language`, choose English, then verify `/help` is in English.
11. Send `/language`, choose Русский, then verify `/help` is in Russian.
12. Start `/new`, then send `/cancel` and verify the flow exits.
13. Set `/timezone` to `Asia/Almaty`.
14. Create a near-due reminder through `/new`.
15. Wait for worker delivery.
16. Check `/list` and verify `next_run_at` advanced.
17. Use `/pause`, tap an inline reminder button, then verify `/list` shows it paused.
18. Use `/resume`, tap an inline reminder button, then verify `/list` shows it active.
19. Use `/delete`, tap a reminder button, cancel once, then repeat and confirm deletion.
20. Verify the deleted reminder disappears from `/list`.

Expected runtime behavior:

- Telegram command menu shows current commands including `/language` and `/cancel`;
- `/language` persists Russian, Kazakh and English interface choices;
- user-authored reminder title/message text is not auto-translated;
- `/cancel` exits active FSM flows and is friendly when nothing is active;
- `/pause`, `/resume` and `/delete` offer inline reminder buttons while preserving manual number/id input;
- `/delete` asks for inline confirmation before deleting;
- worker sends due active reminders with basic MVP delivery behavior;
- paused reminders are not sent;
- deleted reminders are not sent;
- successful sends create `reminder_deliveries` records;
- failed sends are logged and recorded without crashing the worker;
- delivery wrapper text uses the user's selected interface language;
- retries are not implemented;
- AI translation is not implemented;
- delivery history command is not implemented;
- dashboard and webhook mode are not implemented.
