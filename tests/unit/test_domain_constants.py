from direm.domain.constants import CheckInResponseType, DeliveryStatus, ReminderStatus, ScheduleType


def test_schedule_type_values_are_stable() -> None:
    assert [item.value for item in ScheduleType] == ["interval", "daily"]


def test_reminder_status_values_are_stable() -> None:
    assert [item.value for item in ReminderStatus] == ["active", "paused", "disabled"]


def test_delivery_status_values_are_stable() -> None:
    assert [item.value for item in DeliveryStatus] == ["sent", "failed", "skipped"]


def test_checkin_response_type_values_are_stable() -> None:
    assert [item.value for item in CheckInResponseType] == ["done", "later", "skipped"]
