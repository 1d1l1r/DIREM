from enum import StrEnum


class ScheduleType(StrEnum):
    INTERVAL = "interval"
    DAILY = "daily"


class ReminderStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class DeliveryStatus(StrEnum):
    SENT = "sent"
    FAILED = "failed"
    SKIPPED = "skipped"


class CheckInResponseType(StrEnum):
    DONE = "done"
    LATER = "later"
    SKIPPED = "skipped"
