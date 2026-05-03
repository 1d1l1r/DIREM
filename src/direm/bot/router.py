from aiogram import Router

from direm.bot.handlers import bunker, cancel, credits, delete, help, language, list, menu, new, pause_resume, start, timezone, version
from direm.bot.middlewares import DatabaseSessionMiddleware


def build_router() -> Router:
    router = Router(name="direm")
    router.message.middleware(DatabaseSessionMiddleware())
    router.callback_query.middleware(DatabaseSessionMiddleware())
    router.include_router(cancel.router)
    router.include_router(start.router)
    router.include_router(menu.router)
    router.include_router(bunker.router)
    router.include_router(help.router)
    router.include_router(language.router)
    router.include_router(timezone.router)
    router.include_router(new.router)
    router.include_router(list.router)
    router.include_router(pause_resume.router)
    router.include_router(delete.router)
    router.include_router(version.router)
    router.include_router(credits.router)
    return router
