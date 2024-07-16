import json
import logging

from nameko.events import EventDispatcher, event_handler
from nameko.timer import timer
from nameko_sqlalchemy import Database
from nameko.web.handlers import http

from core import request_schemas, response_schemas, events
from core.dependencies import MemoryStore, Auth
from core.models.base import DeclarativeBase

from core.services.user import UserService
from core.repositories.user import UserRepository

from core.services.currency import CurrencyService
from core.repositories.currency import CurrencyRepository

from core.services.transaction import TransactionService
from core.repositories.transaction import TransactionRepository

_logger = logging.getLogger(__name__)


class CoreController:
    name = 'core'

    memory_store = MemoryStore()
    db = Database(DeclarativeBase, engine_options={
        'pool_pre_ping': True,
        'pool_size': 100,
        'max_overflow': 100,
    })
    auth = Auth()
    dispatch = EventDispatcher()

    @http('GET', '/health')
    def health_check(self, request):
        return 200, json.dumps({})

    @http('POST', '/users')
    def create_user(self, request):
        data = request_schemas.UserSchema().load(request.get_json())
        user_service = self._get_user_service({})
        response = user_service.create_user(
            data=data,
        )
        return response_schemas.UserSchema().dumps(response)

    @http('POST', '/tokens')
    def authenticate(self, request):
        data = request_schemas.AuthenticateSchema().load(request.get_json())
        user_service = self._get_user_service({})
        response = user_service.authenticate(
            data=data,
        )
        return response_schemas.AuthenticateSchema().dumps(response)

    @auth.token_required
    @http('GET', '/currencies')
    def list_currencies(self, request):
        currency_service = self._get_currency_service(request.access_info)
        response = currency_service.list_currencies()
        return response_schemas.CurrencySchema(many=True).dumps(response)

    @auth.token_required
    @http('POST', '/transactions')
    def submit_transaction(self, request):
        data = request_schemas.SubmitTransactionSchema().load(request.get_json())
        transaction_service = self._get_transaction_service(request.access_info)
        response = transaction_service.submit_transaction(
            data=data,
        )
        return response_schemas.TransactionSchema().dumps(response)

    @event_handler('core', events.SettlementWithExchange.event_name)
    def handle_exchange_settle(
            self, payload
    ):
        # This method consume the settlement with exchange event to settle with exchange
        _logger.debug(
            f"EVENT CONSUME:"
            f" {str(payload)}"
        )
        access_info = payload.get('access_info')
        transaction_service = self._get_transaction_service(
            access_info=access_info,
        )
        transaction_service.settle_with_exchange()

    @timer(interval=3600)  # One Hour
    def settling_transaction_garbage_collector(self):
        # This method is called every hour to revert transactions to the SUBMITTED state
        # for any reason that are stuck in the SETTLING state.
        transaction_service = self._get_transaction_service({})
        transaction_service.settling_transaction_garbage_collector()

    def _get_user_service(self, access_info):
        user_repo = UserRepository(self.db.session)

        return UserService(
            access_info=access_info,
            user_repo=user_repo,
            memory_store=self.memory_store,
        )

    def _get_currency_service(self, access_info):
        currency_repo = CurrencyRepository(self.db.session)

        return CurrencyService(
            access_info=access_info,
            currency_repo=currency_repo,
        )

    def _get_transaction_service(self, access_info):
        transaction_repo = TransactionRepository(self.db.session)
        currency_repo = CurrencyRepository(self.db.session)

        return TransactionService(
            access_info=access_info,
            currency_repo=currency_repo,
            transaction_repo=transaction_repo,
            dispatch=self.dispatch,
        )
