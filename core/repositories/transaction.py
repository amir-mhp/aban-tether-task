from sqlalchemy import func

from core.entities.transaction import TransactionEntity
from core.entities.user import UserEntity
from core.repositories.base import BaseStoreRepository, SQLAlchemyStore


class TransactionRepository(BaseStoreRepository):

    def __init__(self, db_session):
        super().__init__()
        self._sqlalchemy_store = SQLAlchemyStore(db_session)

        self._stores = [
            self._sqlalchemy_store,
        ]

    def get_user_with_lock(self, user_id) -> UserEntity:
        with self:
            user = self._sqlalchemy_store.session.query(
                UserEntity
            ).filter(
                UserEntity.id == user_id
            ).with_for_update(nowait=True).one()

            return user

    def update_user_balance(self, entity: UserEntity):
        with self:
            self._sqlalchemy_store.session.add(entity)

    def create_transaction(self, entity: TransactionEntity):
        with self:
            self._sqlalchemy_store.session.add(entity)

    def get_total_transaction_amount(self):
        with self:
            total_amount = self._sqlalchemy_store.session.query(
                func.sum(
                    TransactionEntity.amount,
                )
            ).filter(
                TransactionEntity.state == TransactionEntity.TransactionState.SUBMITTED
            ).scalar()

            return total_amount if total_amount else 0

    def list_transaction(self, state=None):
        with self:
            query = self._sqlalchemy_store.session.query(TransactionEntity)

            if state:
                query = query.filter(
                    TransactionEntity.state == state,
                )

            return query.all()

    def list_transaction_with_lock(self, state):
        with self:
            query = self._sqlalchemy_store.session.query(TransactionEntity)

            if state:
                query = query.filter(
                    TransactionEntity.state == state,
                )

            return query.with_for_update().all()

    def update_transactions_into_settling(self, ids):
        with self:
            self._sqlalchemy_store.session.query(
                TransactionEntity,
            ).filter(
                TransactionEntity.id.in_(ids),
                TransactionEntity.state == TransactionEntity.TransactionState.SUBMITTED
            ).update(
                {TransactionEntity.state: TransactionEntity.TransactionState.SETTLING},
                synchronize_session='fetch',
            )

    def update_transactions_into_settled(self, ids):
        with self:
            self._sqlalchemy_store.session.query(
                TransactionEntity,
            ).filter(
                TransactionEntity.id.in_(ids),
                TransactionEntity.state == TransactionEntity.TransactionState.SETTLING,
            ).update(
                {TransactionEntity.state: TransactionEntity.TransactionState.SETTLED},
                synchronize_session='fetch',
            )

    def update_transactions_into_from_settling_to_submitted(self):
        with self:
            self._sqlalchemy_store.session.query(
                TransactionEntity,
            ).filter(
                TransactionEntity.state == TransactionEntity.TransactionState.SETTLING,
            ).update(
                {TransactionEntity.state: TransactionEntity.TransactionState.SUBMITTED},
                synchronize_session='fetch',
            )
