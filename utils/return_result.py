from flask import jsonify, make_response
from utils.error_cause import ErrorCause


def ok(result=None) -> str:
    if result is None:
        result = {}
    return jsonify({
        "error_code": 0,
        "result": result
    })


def error(cause: ErrorCause, reason: str = "") -> str:
    return make_response(jsonify({
        "error_code": cause.value[0],
        "error_message": cause.value[1],
        "reason": reason
    }), cause.value[2])
