from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from direm.domain.constants import CheckInResponseType
from direm.i18n import t


CHECKIN_CALLBACK_PREFIX = "checkin"


def checkin_keyboard(language_code: str | None, delivery_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(language_code, "checkin.button.done"),
                    callback_data=build_checkin_callback_data(delivery_id, CheckInResponseType.DONE.value),
                ),
                InlineKeyboardButton(
                    text=t(language_code, "checkin.button.later"),
                    callback_data=build_checkin_callback_data(delivery_id, CheckInResponseType.LATER.value),
                ),
                InlineKeyboardButton(
                    text=t(language_code, "checkin.button.skipped"),
                    callback_data=build_checkin_callback_data(delivery_id, CheckInResponseType.SKIPPED.value),
                ),
            ]
        ]
    )


def build_checkin_callback_data(delivery_id: int, response_type: str) -> str:
    return f"{CHECKIN_CALLBACK_PREFIX}:{delivery_id}:{response_type}"


def parse_checkin_callback_data(data: str | None) -> tuple[int, str] | None:
    if not data:
        return None

    parts = data.split(":")
    if len(parts) != 3 or parts[0] != CHECKIN_CALLBACK_PREFIX:
        return None

    _, delivery_id_raw, response_type_raw = parts
    if not delivery_id_raw.isdigit():
        return None

    delivery_id = int(delivery_id_raw)
    if delivery_id <= 0:
        return None

    try:
        response_type = CheckInResponseType(response_type_raw).value
    except ValueError:
        return None

    return delivery_id, response_type
