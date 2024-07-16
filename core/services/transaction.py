import datetime
import json
import logging
import uuid
from sqlite3 import IntegrityError

from nameko import config

from core import response_schemas, events
from core.entities.transaction import TransactionEntity
from core.exchange.base import get_exchanges
from core.repositories.transaction import TransactionRepository
from core.repositories.currency import CurrencyRepository

logger = logging.getLogger(__name__)


class TransactionService:

    def __init__(
            self,
            access_info,
            currency_repo: CurrencyRepository,
            transaction_repo: TransactionRepository,
            dispatch,
    ):
        self.access_info = access_info
        self.currency_repo = currency_repo
        self.transaction_repo = transaction_repo
        self.dispatch = dispatch

    def submit_transaction(self, data):
        currency_id = data['currency_id']
        count = data['count']

        currency = self.currency_repo.get_currency_with_id(currency_id=currency_id)

        if not currency:
            raise Exception("Currency not found!")

        with self.transaction_repo as repo:
            try:
                user_id = self.access_info['user']['id']
                user = repo.get_user_with_lock(user_id)

                amount = float(currency.price * count)

                if user.wallet_balance < amount:
                    raise ValueError("Insufficient balance")

                user.wallet_balance -= amount

                repo.update_user_balance(user)
                repo.create_transaction(
                    TransactionEntity(
                        user_id=user_id,
                        currency_id=currency.id,
                        count=count,
                        amount=amount,
                        state=TransactionEntity.TransactionState.SUBMITTED,
                    )
                )

                repo._sqlalchemy_store.session.commit()

                events.SettlementWithExchange().send(
                    dispatch=self.dispatch,
                    access_info=self.access_info,
                )

                logger.info(f"Transaction successful, access_info: {self.access_info}")

                return {
                    "user": user,
                    "amount": amount,
                    "currency": currency,
                }
            except IntegrityError as e:
                repo._sqlalchemy_store.session.rollback()
                logger.error(f"Transaction failed: {e}, access_info: {self.access_info}")
                raise e
            except Exception as e:
                repo._sqlalchemy_store.session.rollback()
                logger.error(f"Error: {e}, access_info: {self.access_info}")
                raise e

    def settle_with_exchange(self):
        list_exchanges = get_exchanges()
        total_amount = self.transaction_repo.get_total_transaction_amount()

        if total_amount < 10000:
            logger.error(f"Not ready for settle - total amount = {total_amount}")
            return

        try:
            # Start a transaction
            with self.transaction_repo as repo:
                transactions = repo.list_transaction_with_lock(
                    state=TransactionEntity.TransactionState.SUBMITTED,
                )

                transaction_ids = []
                total_amount = 0
                for transaction in transactions:
                    transaction_ids.append(transaction.id)

                    # Maybe total amount updated!
                    total_amount += transaction.amount

                repo.update_transactions_into_settling(ids=transaction_ids)

                for exchange in list_exchanges:
                    exchange = exchange()
                    if exchange.is_ready():
                        token = exchange.get_token(
                            username="",
                            password="",
                        )
                        exchange.buy_from_exchange(
                            token=token,
                            amount=total_amount,
                        )
                        break

                repo.update_transactions_into_settled(ids=transaction_ids)
                logger.info(f"Transactions set to settled: {transaction_ids}")
        except Exception as e:
            logger.error(f"Error during settlement: {e}")
            raise

    def settling_transaction_garbage_collector(self):
        self.transaction_repo.update_transactions_into_from_settling_to_submitted()
