from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


DEFAULT_ERROR_MESSAGES = {
    "validation_error": _("Please review the submitted data."),
    "authentication_failed": _(
        "Invalid credentials. Please verify your email and password."
    ),
    "not_authenticated": _("Authentication credentials were not provided."),
    "permission_denied": _("You do not have permission to perform this action."),
    "not_found": _("The requested resource was not found."),
    "method_not_allowed": _("This HTTP method is not allowed for this endpoint."),
    "throttled": _("Too many requests. Please try again in a moment."),
    "parse_error": _("The request payload could not be processed."),
    "server_error": _("An unexpected server error occurred."),
}


def _normalize_error_detail(detail, fallback_code="error"):
    if isinstance(detail, ErrorDetail):
        return {
            "code": str(detail.code or fallback_code),
            "message": str(detail),
        }

    if isinstance(detail, list):
        return [_normalize_error_detail(item, fallback_code) for item in detail]

    if isinstance(detail, dict):
        return {
            key: _normalize_error_detail(value, fallback_code)
            for key, value in detail.items()
        }

    return {
        "code": fallback_code,
        "message": str(detail),
    }


def _extract_message(normalized_detail, default_message):
    if isinstance(normalized_detail, dict):
        if "message" in normalized_detail and isinstance(
            normalized_detail["message"], str
        ):
            return normalized_detail["message"]

        for value in normalized_detail.values():
            message = _extract_message(value, default_message)
            if message:
                return message

    if isinstance(normalized_detail, list):
        for item in normalized_detail:
            message = _extract_message(item, default_message)
            if message:
                return message

    return default_message


def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is None:
        return Response(
            {
                "code": "server_error",
                "message": str(DEFAULT_ERROR_MESSAGES["server_error"]),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(response.data, list):
        code = "validation_error"
        normalized_errors = _normalize_error_detail(response.data, code)
        message = _extract_message(normalized_errors, str(DEFAULT_ERROR_MESSAGES[code]))
        response.data = {
            "code": code,
            "message": message,
            "errors": normalized_errors,
        }
        return response

    if isinstance(response.data, dict):
        normalized_codes = exc.get_codes() if hasattr(exc, "get_codes") else {}
        normalized_errors = _normalize_error_detail(
            response.data,
            "error",
        )

        if "detail" in response.data:
            code = (
                str(normalized_codes) if isinstance(normalized_codes, str) else "error"
            )
            message = _extract_message(
                normalized_errors.get("detail"),  # type: ignore[arg-type]
                str(DEFAULT_ERROR_MESSAGES.get(code, response.data["detail"])),
            )
            response.data = {
                "code": code,
                "message": message,
            }
            return response

        code = "validation_error"
        message = _extract_message(normalized_errors, str(DEFAULT_ERROR_MESSAGES[code]))
        response.data = {
            "code": code,
            "message": message,
            "errors": normalized_errors,
        }
        return response

    response.data = {
        "code": "error",
        "message": str(response.data),
    }
    return response
