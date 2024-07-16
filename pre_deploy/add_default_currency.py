import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
import os

import walrus
import yaml

from nameko import config
from nameko.cli.utils.config import env_var_constructor, IMPLICIT_ENV_VAR_MATCHER
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as BaseSession
from sqlalchemy.orm import sessionmaker

from functools import partial

from core.repositories import currency as currency_repo

logging.basicConfig(level=logging.INFO)

dt_fmt = "%Y-%m-%dT%H:%M:%SZ"

currencies = [
    {"title": "ABAN", "price": 1000},
]


def load_config(config_path):
    yaml.add_constructor('!env_var', env_var_constructor, yaml.UnsafeLoader)
    yaml.add_constructor('!raw_env_var', partial(env_var_constructor, raw=True), yaml.UnsafeLoader)  # noqa
    yaml.add_implicit_resolver('!env_var', IMPLICIT_ENV_VAR_MATCHER, Loader=yaml.UnsafeLoader)
    with open(config_path) as fle:
        _configs = yaml.unsafe_load(fle)
    return _configs


def _setup_config():
    parent_path = os.path.dirname(os.path.dirname(__file__))
    config_file = os.getenv("NAMEKO_CONFIG_FILE", parent_path + '/config.yml')
    if not config_file or not os.path.exists(config_file):
        raise RuntimeError("'NAMEKO_CONFIG_FILE' environment variable is not set")

    _configs = load_config(config_file)

    config.setup(_configs)
    logging.info(f"Config loaded: {config}")
    return _configs


configs = _setup_config()


class CoreSession(BaseSession):
    def __init__(self, *args, **kwargs):
        self.close_on_exit = kwargs.pop('close_on_exit', False)
        super(CoreSession, self).__init__(*args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:
                self.rollback()
            else:
                try:
                    self.commit()
                except Exception:
                    self.rollback()
                    raise
        finally:
            if self.close_on_exit:
                self.close()


def get_session():
    engine = create_engine(configs['DB_URIS']['core:Base'], echo=False)
    Session = sessionmaker(bind=engine, class_=CoreSession)
    _session = Session()
    return _session


def get_currencies_repo(session):
    return currency_repo.CurrencyRepository(session)


def do_sync():
    try:
        session = get_session()

        currencies_repo = get_currencies_repo(session)

        for currency in currencies:
            session.add(
                currency_repo.CurrencyEntity(
                    title=currency.get("title"),
                    price=currency.get("price"),
                )
            )
            logging.info("Category added -> ", currency)
            session.commit()

    except Exception as exp:
        logging.exception(exp)
    else:
        logging.info("Synchronization is finished successfully")


def main():
    logging.info("--- Add Categories ---")
    do_sync()


if __name__ == '__main__':
    main()
