import dataclasses
import traceback
import logging
from typing import Optional, List

_logger = logging.getLogger(__name__)


class BaseEvent:
    event_name = None

    def send(self, dispatch, access_info):
        try:
            dispatch(self.event_name, {
                'EVENT_NAME': self.event_name,
                'body': dataclasses.asdict(self),
                'access_info': access_info,
            })
            _logger.debug(f"Event dispatched: {self.event_name}")
        except Exception as exp:
            _logger.error(
                f'Unable to dispatch {self.event_name} event because:'
                f' {str(exp)}: {traceback.format_exc()}'
            )


@dataclasses.dataclass
class SettlementWithExchange(BaseEvent):
    """
    This event should be raised whenever settle with exchange!
    """
    event_name = "SETTLEMENT_WITH_EXCHANGE"
