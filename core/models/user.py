from sqlalchemy import Table, Column, String, FLOAT
from sqlalchemy.orm import mapper

from core.entities.user import UserEntity
from core.models.base import uuid_pk_column, meta, temporal_columns, PhoneField

users = Table(
    'users', meta,
    uuid_pk_column(),
    Column('phone', PhoneField, nullable=True, default=None, unique=True),
    Column('password', String(255), nullable=False),
    Column('first_name', String(32), nullable=True, default=None),
    Column('last_name', String(32), nullable=True, default=None),
    Column('wallet_balance', FLOAT, nullable=False, default='0'),
    *temporal_columns()
)

mapper(
    UserEntity,
    users,
)
