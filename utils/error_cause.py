from enum import Enum, unique


@unique
class ErrorCause(Enum):
    NOT_AUTHORIZED = (1, "Not Authorized")
    LOGIN_FAILED = (2, "Login Failed")
    USER_EXISTED = (3, "User Existed")
    CONTENT_NOT_EXISTED = (4, "Content Not Existed")
    NO_MORE_CONTENT = (5, "No More Content")
    REQUEST_INVALID = (6, "Request Invalid")
    REQUEST_INCOMPLETE = (7, "Request Incomplete")
