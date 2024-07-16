import datetime
import typing
from dataclasses import dataclass, field

from core.utils import now


@dataclass
class CurrencyEntity:
    title: str
    price: int

    id: typing.Optional[str] = None

    created_at: typing.Optional[datetime.datetime] = field(default_factory=now)
    updated_at: typing.Optional[datetime.datetime] = field(default_factory=now)
    deleted_at: typing.Optional[datetime.datetime] = None
