from app.lib.schemas import error_response

COMMON_RESPONSES = {
    401: {
        "model": error_response.UnauthorizedError,
        "summary": "Unauthorized - Check API Token",
    },
    422: {"model": error_response.ValidationError, "summary": "Validation error"},
    500: {"model": error_response.ErrorResponse, "summary": "Internal Server Error"},
    503: {"model": error_response.ErrorResponse, "summary": "Service Unavailable"},
}
