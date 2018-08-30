import secrets
import hashlib
from functools import wraps

import config
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


def generate_token() -> str:
    new_token = secrets.token_hex(16)

    while db.users.find_one({'token': new_token}) is not None:
        new_token = secrets.token_hex(16)

    return new_token


def generate_uid() -> int:
    new_uid = secrets.randbits(31)

    while db.users.find_one({'_id': new_uid}) is not None:
        new_uid = secrets.randbits(31)

    return new_uid


def hash_password(password: str) -> str:
    salted_password = password + config.PASSWORD_SALT
    return hashlib.sha256(salted_password.encode()).hexdigest()
