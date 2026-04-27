from aiogram.fsm.state import State, StatesGroup


class TimezoneFlow(StatesGroup):
    waiting_for_timezone = State()


class CreateReminderFlow(StatesGroup):
    waiting_title = State()
    waiting_message_text = State()
    waiting_schedule_type = State()
    waiting_interval_minutes = State()
    waiting_daily_time = State()
    waiting_active_window_choice = State()
    waiting_active_window_value = State()
    waiting_confirmation = State()


class ReminderControlFlow(StatesGroup):
    waiting_pause_selection = State()
    waiting_resume_selection = State()
    waiting_delete_selection = State()
    waiting_delete_confirmation = State()
