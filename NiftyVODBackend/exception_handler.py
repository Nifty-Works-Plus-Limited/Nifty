import json
from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(error, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(error, context)

    # Now add the HTTP status code to the response.
    if response is not None:

        error_payload = {
          "status": "error",
          "code": response.status_code,
          "message": response.data,
          "data": None,
        }
        response.data = error_payload
        

    return response