import datetime
import json
import uuid

from nameko import config

from core import response_schemas
from core.entities.currency import CurrencyEntity
from core.hashers import make_password, check_password
from core.repositories.currency import CurrencyRepository


class CurrencyService:

    def __init__(
            self,
            access_info,
            currency_repo: CurrencyRepository,
    ):
        self.access_info = access_info
        self.currency_repo = currency_repo

    def list_currencies(self):
        return self.currency_repo.list_currencies()
