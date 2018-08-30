from flask import jsonify
from utils.error_cause import ErrorCause


def ok(result="OK") -> str:
    return jsonify({
        "error_code": 0,
        "result": result
    })


def error(cause: ErrorCause, reason: str = "") -> str:
    return jsonify({
        "error_code": cause.value[0],
        "error_message": cause.value[1],
        "reason": reason
    })
