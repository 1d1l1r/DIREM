import asyncio
import logging

from sqlalchemy.exc import SQLAlchemyError

from direm.bot.checkin_buttons import checkin_keyboard
from direm.db.session import async_session_factory
from direm.repositories.deliveries import ReminderDeliveryRepository
from direm.repositories.reminders import ReminderRepository
from direm.services.reminder_delivery_service import ReminderDeliveryService, TelegramSender

logger = logging.getLogger(__name__)


async def run_worker(sender: TelegramSender, *, poll_seconds: int, batch_size: int) -> None:
    logger.info("Starting DIREM worker delivery loop.")
    schema_warning_logged = False
    while True:
        async with async_session_factory() as session:
            try:
                service = ReminderDeliveryService(
                    ReminderRepository(session),
                    ReminderDeliveryRepository(session),
                    sender,
                    checkin_markup_factory=checkin_keyboard,
                )
                delivered_count = await service.deliver_due_once(limit=batch_size)
                await session.commit()
                logger.info("Worker delivery poll complete: delivered=%s", delivered_count)
                schema_warning_logged = False
            except SQLAlchemyError as exc:
                await session.rollback()
                if _is_missing_schema_error(exc):
                    if not schema_warning_logged:
                        logger.warning("Worker database schema is not ready yet. Run Alembic migrations before runtime smoke.")
                        schema_warning_logged = True
                    else:
                        logger.debug("Worker database schema is still not ready.")
                else:
                    logger.exception("Worker delivery poll failed.")
            except Exception:
                await session.rollback()
                logger.exception("Worker delivery poll failed.")

        await asyncio.sleep(poll_seconds)


def _is_missing_schema_error(error: SQLAlchemyError) -> bool:
    message = str(error).lower()
    return ("relation" in message and "does not exist" in message) or "no such table" in message
