"""Exceptions for the repository module."""
from thipster.engine import THipsterError


class ModelNotFoundError(THipsterError):
    """Exception raised when a model is not found in the database."""

    def __init__(self, model: str, *args) -> None:
        super().__init__(*args)
        self.model = model

    @property
    def message(self):
        """Return the exception message."""
        return f"Couldn't find {self.model} model"
