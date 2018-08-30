from functools import wraps

from utils.error_cause import ErrorCause
from utils.return_result import error
from .database_helper import db
from flask import request


def require_token(func):

    auth_header_name = 'Authorization'

    @wraps(func)
    def check_token(*args, **kwargs):

        headers = request.headers
        if auth_header_name not in headers.keys():
            return error(ErrorCause.NOT_AUTHORIZED)

        token = headers[auth_header_name].split(' ')[1]
        user = db.users.find_one({
            'token': token
        })
        if user is None:
            return error(ErrorCause.NOT_AUTHORIZED)

        return func(user, *args, **kwargs)

    return check_token


