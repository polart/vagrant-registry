from rest_framework import status
from rest_framework.exceptions import APIException


class CustomApiException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid input'
    default_code = 'error'

    def __init__(self, detail=None, code=None, status_code=None):
        if status_code is None:
            self.status_code = status_code
        super().__init__(detail, code)
