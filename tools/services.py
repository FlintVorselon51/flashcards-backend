from abc import ABC, abstractmethod

from rest_framework.response import Response


class AbstractService(ABC):
    """Use this class to define new services"""

    @abstractmethod
    def execute(self) -> Response:
        """Service logic is described here."""
        return self._form_successful_response()

    @abstractmethod
    def _form_successful_response(self) -> Response:
        pass
