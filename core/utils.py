import datetime
import uuid


def is_valid_uuid(uuid_str):
    try:
        if isinstance(uuid_str, uuid.UUID):
            return True
        else:
            uuid_obj = uuid.UUID(uuid_str)
            return str(uuid_obj) == uuid_str
    except ValueError:
        return False


def now():
    return datetime.datetime.now(datetime.timezone.utc)
