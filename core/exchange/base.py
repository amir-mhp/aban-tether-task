import abc


class BaseExchangeService(abc.ABC):
    @abc.abstractmethod
    def get_token(self, username, password):
        raise NotImplementedError

    @abc.abstractmethod
    def buy_from_exchange(self, token, amount):
        raise NotImplementedError

    @abc.abstractmethod
    def is_ready(self, *args, **kwargs):
        raise NotImplementedError


def get_exchanges():
    subclasses = BaseExchangeService.__subclasses__()

    # Sort subclasses by the 'order' attribute
    sorted_subclasses = sorted(subclasses, key=lambda x: getattr(x, 'order', float('inf')))

    return sorted_subclasses
