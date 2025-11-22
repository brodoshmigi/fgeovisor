import logging
from copy import copy

from staff.interfaces.error.state_interface import ErrorState

logger = logging.getLogger(__name__)

class ErrorSnapshot(ErrorState):

    ERRORS_WORDBOOK = {
        "auth_check": False,
        "is_staff": False,
        "is_vallid_error": False,
        "login_error": False,
        "create_error": False,
        "photo": False
    }

    def __init__(self):
        self._current_state = copy(self.ERRORS_WORDBOOK)

    def _get_current_state(self):
        return self._current_state
    
    def _reset(self):
        self._current_state = copy(self.ERRORS_WORDBOOK)

    def set_error(self, error_key: str, value: bool = True) -> None:
        if error_key in self._current_state:
            self._current_state[error_key] = value
        else:
            logger.warning("%s is not supported: ", error_key)

    def send(self):
        final_wordbook = self._get_current_state()
        self._reset()
        return final_wordbook