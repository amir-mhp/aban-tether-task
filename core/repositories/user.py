from core.entities.user import UserEntity
from core.repositories.base import BaseStoreRepository, SQLAlchemyStore


class UserRepository(BaseStoreRepository):

    def __init__(self, db_session):
        super().__init__()
        self._sqlalchemy_store = SQLAlchemyStore(db_session)

        self._stores = [
            self._sqlalchemy_store,
        ]

    def create_user(
            self,
            entity: UserEntity,
    ):
        with self as session:
            session.add(entity)

    def get_user_by_phone(self, phone):
        return self._sqlalchemy_store.session.query(UserEntity).filter(
            UserEntity.phone == phone,
            UserEntity.deleted_at.is_(None),
        ).first()
