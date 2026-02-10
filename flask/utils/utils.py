from datetime import datetime, timedelta, timezone
import secrets

class Utils():
    def __init__(self):
        pass

    ############################################
    #_______________DATETIME___________________#
    ############################################

    def format_datetime(self, dt):
        if dt is None:
            return "—"

        if isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt)
            except ValueError:
                return dt

        return dt.astimezone().strftime("%d %b %Y at %H:%M")
    
    def get_datetime_utc(self):
        return datetime.now(timezone.utc)

    def get_datetime_isoformat(self):
        return datetime.now(timezone.utc).isoformat()

    def get_datetime_plus_timedelta(self, timedelta_days= 0, timedelta_hours=0, timedelta_minutes=0):
        return self.get_datetime + timedelta(days=timedelta_days,
                                                       hours=timedelta_hours,
                                                       minutes=timedelta_minutes)
    
    def datetime_is_expired_minutes(self, datetime_created, timedelta_minutes):
        return datetime.now(timezone.utc) > datetime_created + timedelta(minutes=timedelta_minutes)
    
    ############################################
    #_______________PASSWORD___________________#
    ############################################

    def generate_password(self, size:int) -> str:
        return secrets.token_urlsafe(size)
    
