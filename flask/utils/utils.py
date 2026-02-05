from datetime import datetime, timedelta, timezone

class Utils():
    def __init__(self):
        pass

    def get_datetime(self):
        return datetime.now(timezone.utc)

    def get_datetime_isoformat(self):
        return datetime.now(timezone.utc).isoformat()
    
    def datetime_is_expired_minutes(self, datetime_created, timedelta_minutes):
        return datetime.now(timezone.utc) > datetime_created + timedelta(minutes=timedelta_minutes)
