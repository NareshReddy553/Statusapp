"""This module contains custom exceptions."""
from typing import Union


class DuplicateUsernameError(Exception):
    """Custom Exception for Duplicate username error.

    Attributes:
        params : Error object which will be received from database.
        message : Message can be a single error, a list of errors, or a
        dictionary that maps field names to lists of errors.
    """

    def __init__(self, message: str, code: str, params: Union[dict, bytes]):
        """Error response object initialization."""
        super(DuplicateUsernameError, self).__init__(message, code, params)
        self.params = params
