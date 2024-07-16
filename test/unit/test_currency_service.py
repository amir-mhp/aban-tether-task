import pytest
from unittest.mock import MagicMock
from core.services.currency import CurrencyService
from core.repositories.currency import CurrencyRepository


@pytest.fixture
def currency_repo():
    return MagicMock(CurrencyRepository)


@pytest.fixture
def currency_service(currency_repo):
    access_info = {}
    return CurrencyService(access_info=access_info, currency_repo=currency_repo)


class TestCurrencies:
    def test_list_currencies(self, currency_service, currency_repo):
        mock_currencies = [
            {'title': 'A', 'price': '1000'},
            {'title': 'B', 'price': '2000'}
        ]
        currency_repo.list_currencies.return_value = mock_currencies

        currencies = currency_service.list_currencies()

        assert currencies == mock_currencies
        currency_repo.list_currencies.assert_called_once()
