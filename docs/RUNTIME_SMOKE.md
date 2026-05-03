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
8. For a fresh Telegram user or reset local database, verify `/start` shows first-run guidance toward `/language`, `/timezone`, `/new` and `/help`.
9. Check that Telegram shows the command menu with `/language` and `/cancel`.
10. Send `/language`, choose Қазақша, then verify `/help` is in Kazakh.
11. Send `/language`, choose English, then verify `/help` is in English.
12. Send `/language`, choose Русский, then verify `/help` is in Russian.
13. Send `/start` as an existing user, verify the localized main menu appears.
14. Tap List, then Back/Home.
15. Tap Settings, then Language, then `/cancel`.
16. Send `/start`, tap Settings, then Timezone, then `/cancel`.
17. Send `/start`, tap Help, then DIREM version.
18. Send `/start`, tap Help, then Credits.
19. Start `/new`, verify the localized Cancel reply button appears, tap it and verify the flow exits.
20. Send `/timezone`, tap `Asia/Almaty`, then verify it is saved.
21. Send `/timezone`, tap manual input, send `Europe/London`, then verify it is saved.
22. Send `/timezone`, send an invalid timezone, then verify the recovery text is clear and `/cancel` exits.
23. Set `/timezone` back to `Asia/Almaty`.
24. Create a near-due reminder through `/new`.
25. Wait for worker delivery.
26. Check `/list` and verify `next_run_at` advanced.
27. Use `/pause`, tap an inline reminder button, then verify `/list` shows it paused.
28. Use `/resume`, tap an inline reminder button, then verify `/list` shows it active.
29. Use `/delete`, tap a reminder button, cancel once, then repeat and confirm deletion.
30. Verify the deleted reminder disappears from `/list`.

Expected runtime behavior:

- Telegram command menu shows current commands including `/language` and `/cancel`;
- first-time `/start` shows lightweight guidance without forcing a tutorial;
- existing-user `/start` shows a localized main menu with List, Settings and Help hubs;
- `/language` persists Russian, Kazakh and English interface choices;
- `/timezone` supports common timezone buttons and manual IANA input;
- `/help` is grouped by purpose and does not show internal worker/retry/dashboard/webhook notes;
- idle state shows a localized Help reply button;
- active FSM flows show a localized Cancel reply button;
- Help and Cancel reply buttons behave like `/help` and `/cancel`;
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
