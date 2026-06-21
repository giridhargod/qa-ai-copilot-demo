#services/time_service.py
from datetime import datetime
from zoneinfo import ZoneInfo


class TimeService:

    @staticmethod
    def get_current_ist():

        return datetime.now(
            ZoneInfo("Asia/Kolkata")
        ).strftime(
            "%Y-%m-%d %H:%M:%S IST"
        )