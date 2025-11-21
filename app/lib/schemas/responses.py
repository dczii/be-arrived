from pydantic import BaseModel


class BaseResponse(BaseModel):
    message: str 


# error responses:
class ErrorResponse(BaseResponse):
    code: str


class ValidationError(ErrorResponse):
    model_config = {
        "json_schema_extra": {
            "example": {
                "code": "[VALIDATION_ERROR]",
                "message": "The [parameter] format is invalid.",
            }
        }
    }

class UnauthorizedError(ErrorResponse):
    model_config = {
        "json_schema_extra": {
            "example": {
                "code": "UNAUTHORIZED",
                "message": "Unauthorized. Check your API token.",
            }
        }
    }

class UnavailableServiceError(ErrorResponse):
    model_config = {
        "json_schema_extra": {
            "example": {
                "code": "UNAUTHORIZED",
                "message": "Unauthorized. Check your API token.",
            }
        }
    }
