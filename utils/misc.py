import hashlib
import secrets

import config
from utils.database_helper import db


def generate_token() -> str:
    new_token = secrets.token_hex(16)

    while db.users.find_one({'token': new_token}) is not None:
        new_token = secrets.token_hex(16)

    return new_token


def generate_id() -> int:
    new_uid = secrets.randbits(31)

    while db.users.find_one({'_id': new_uid}) is not None:
        new_uid = secrets.randbits(31)

    return new_uid


def hash_password(password: str) -> str:
    salted_password = password + config.PASSWORD_SALT
    return hashlib.sha256(salted_password.encode()).hexdigest()