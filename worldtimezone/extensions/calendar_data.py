import peewee
import pytz
from typing import Optional
import datetime

FILE_SQLITE_DB = ".data/calendar.db"

db = peewee.SqliteDatabase(FILE_SQLITE_DB)

# START Code from https://compileandrun.com/python-peewee-timezone-aware-datetime/
class TimestampTzField(peewee.Field):
    """
    A timestamp field that supports a timezone by serializing the value
    with isoformat.
    """

    field_type = 'TEXT'  # This is how the field appears in Sqlite

    def db_value(self, value: datetime.datetime) -> str:
        if value:
            return value.isoformat()

    def python_value(self, value: str) -> datetime.datetime:
        if value:
            return datetime.datetime.fromisoformat(value)
# END Code from https://compileandrun.com/python-peewee-timezone-aware-datetime/


class DBBaseModel(peewee.Model):
    class Meta:
        database = db

class DBUser(DBBaseModel):
    discord_id = peewee.CharField(unique=True)

class DBEvent(DBBaseModel):
    title = TextField()
    start = TimestampTzField()
    end = TimestampTzField()
    user = peewee.ForeignKeyField(DBUser, backref="events")
    reminder = TimestampTzField(null=True, default=None)
    number_of_reminder = peewee.IntegerField(default=0)
    minutes_between_reminder = peewee.IntegerField(default=5)

class CalendarData:
    def __init__(self):
        db.connect()
        db.create_tables([DBUser, DBEvent])

    # User

    def create_user(self, user_id) -> DBUser:
        user = DBUser(discord_id=user_id)
        user.save()
        return user

    def get_user(self, user_id) -> Optional[DBUser]:
        try:
            return DBUser.select().where(DBUser.discord_id == user_id).get()
        except DBUser.DoesNotExist:
            return None

    # Event

    def create_event(self, user: DBUser, title: str, start: datetime.datetime, end: datetime.datetime, reminder: Optional[datetime.datetime], number_of_reminder: int = 0, minutes_between_reminder: int = 5):
        event = DBEvent(start=start, end=end, user=user, reminder=reminder, number_of_reminder=number_of_reminder)
        event.save()

    def get_events_list(self, user: DBUser) -> list[DBEvent]:
        return list(user.events)

    def get_events_need_reminder(self) -> list[DBEvent]:
        now = datetime.datetime.now().timestamp()
        return list(DBEvent.select().where(DBEvent.reminder.to_timestamp() < now))

    def set_event_done_reminder(self, events: list[DBEvent]):
        for event in events:
            event.number_of_reminder -= 1
            if event.number_of_reminder == 0:
                event.reminder = None
            else:
                timedelta = datetime.timedelat(minutes=event.minutes_between_reminder)
                event.reminder = event.reminder + timedelta
        DBEvent.bulk_update(events, [DBEvent.number_of_reminder, DBEvent.reminder], batch_size=10)