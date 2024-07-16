import datetime
import typing
from dataclasses import dataclass, field

from core.utils import now


@dataclass
class UserEntity:
    phone: str
    password: str
    first_name: str
    last_name: str

    id: typing.Optional[str] = None
    wallet_balance: typing.Optional[float] = 0

    created_at: typing.Optional[datetime.datetime] = field(default_factory=now)
    updated_at: typing.Optional[datetime.datetime] = field(default_factory=now)
    deleted_at: typing.Optional[datetime.datetime] = None
