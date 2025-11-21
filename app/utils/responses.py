from app.lib.schemas import responses

COMMON_RESPONSES = {
    401: {
        "model": responses.UnauthorizedError,
        "summary": "Unauthorized - Check API Token",
    },
    422: {"model": responses.ValidationError, "summary": "Validation error"},
    500: {"model": responses.ErrorResponse, "summary": "Internal Server Error"},
    503: {
        "model": responses.UnavailableServiceError,
        "summary": "Service Unavailable",
    },
}
