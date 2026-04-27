class ScheduleValidationError(ValueError):
    pass


class InvalidTimezoneError(ScheduleValidationError):
    pass


class InvalidActiveWindowError(ScheduleValidationError):
    pass


class InvalidScheduleConfigError(ScheduleValidationError):
    pass
