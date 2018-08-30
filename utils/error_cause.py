from enum import Enum, unique


@unique
class ErrorCause(Enum):
    NOT_AUTHORIZED = (1, "Not Authorized", 401)
    LOGIN_FAILED = (2, "Login Failed", 403)
    USER_EXISTED = (3, "User Existed", 202)
    CONTENT_NOT_EXISTED = (4, "Content Not Existed", 404)
    NO_MORE_CONTENT = (5, "No More Content", 202)
    REQUEST_INVALID = (6, "Invalid Request", 400)
    REQUEST_INCOMPLETE = (7, "Incomplete Request", 400)
