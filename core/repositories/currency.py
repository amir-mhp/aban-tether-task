from core.entities.currency import CurrencyEntity
from core.utils.utils import is_valid_uuid


class CurrencyRepository:

    def __init__(self, db_session):
        self._db_session = db_session

    def list_currencies(self):
        return self._db_session.query(CurrencyEntity).all()

    def get_currency_with_id(self, currency_id) -> CurrencyEntity:
        if not is_valid_uuid(currency_id):
            raise Exception(f"ID {currency_id} is not a valid id")

        return self._db_session.query(CurrencyEntity).filter(
            CurrencyEntity.id == currency_id,
            CurrencyEntity.deleted_at.is_(None),
        ).first()
