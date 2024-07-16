import requests

from core.exchange.BinX.url import UrlMixin
from core.exchange.base import BaseExchangeService


class BinxService(BaseExchangeService):
    order = 1
    base_url = 'https://google.com'

    def get_token(self, username, password):
        return requests.post(f"{self.base_url}{UrlMixin.LOGIN}", json={
            "username": username,
            "password": password,
        })

    def buy_from_exchange(self, token, amount):
        return requests.post(f"{self.base_url}{UrlMixin.SETTLE_WITH_EXCHANGE}", json={
            "amount": amount,
        }, headers={"Authorization": f"Bearer {token}"})

    def is_ready(self):
        return True
