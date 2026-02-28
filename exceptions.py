class WeekPlannerException(Exception):
    """Base exception for WeekPlanner errors."""


class WeekPlannerInitException(WeekPlannerException):
    """Exception for errors during the initialization of the WeekMenuPlanner."""


class WeekPlannerSaveException(WeekPlannerException):
    """Exception for save to database errors."""
