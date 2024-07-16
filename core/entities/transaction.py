import datetime
import enum
import typing
from dataclasses import dataclass, field

from core.utils.utils import now


@dataclass
class TransactionEntity:
    class TransactionState(enum.Enum):
        SUBMITTED = 'SUBMITTED'
        SETTLING = 'SETTLING'
        SETTLED = 'SETTLED'

    user_id: str
    currency_id: str
    count: str
    amount: str
    state: TransactionState = TransactionState.SUBMITTED

    id: typing.Optional[str] = None

    created_at: typing.Optional[datetime.datetime] = field(default_factory=now)
    updated_at: typing.Optional[datetime.datetime] = field(default_factory=now)
    deleted_at: typing.Optional[datetime.datetime] = None
