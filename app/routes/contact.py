import httpx
from fastapi import APIRouter, status, HTTPException
from app.configs import env
from app.lib.schemas import contact
from datetime import datetime
from app.utils.responses import COMMON_RESPONSES

contact_router = APIRouter()

INTERCOM_URL = "https://api.intercom.io/contacts"
INTERCOM_HEADERS = {
    "Content-type": "application/json",
    "Intercom-Version": "2.14",
    "Authorization": f"Bearer {env.intercom_access_token}",
}


# no response model for now
@contact_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Retrieve a paginated list of contacts",
    # include all error responses for docks except 422
    responses={k: v for k, v in COMMON_RESPONSES.items() if k != 422},
)
async def get_all_contacts():
    try:
        async with httpx.AsyncClient(headers=INTERCOM_HEADERS) as client:
            response = await client.get(INTERCOM_URL)
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as err:
        try:
            error_data = err.response.json()
            errors_list = error_data.get("errors", [])
            error = errors_list[0] if errors_list else {}

            error_code = error.get("code", "INTERCOM_ERROR")
            error_msg = error.get("message", str(err))
        except Exception:
            error_code = "INTERCOM_ERROR"
            error_msg = err.response.text

        raise HTTPException(
            status_code=err.response.status_code,
            detail={"code": error_code, "message": error_msg},
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "SERVICE_UNAVAILABLE", "message": "Can't reach Intercom."},
        )

    except Exception as err:
        # simple error handler for now
        print(f"Unexpected error occurred: {str(err)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="INTERNAL_ERROR",
            message="Internal server error.",
        )


# required arguments for now and no response model for now
@contact_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a contact",
    responses={
        **COMMON_RESPONSES, #include all error responses
    },
)
async def create_contact(contact_data: contact.ContactCreate):
    payload = contact_data.model_dump()

    current_timestamp = int(datetime.now().timestamp())
    payload["signed_up_at"] = current_timestamp
    payload["last_seen_at"] = current_timestamp

    try:
        async with httpx.AsyncClient(headers=INTERCOM_HEADERS) as client:
            response = await client.post(INTERCOM_URL, json=payload)
            response.raise_for_status()  # only for 4xx-5xx
            return response.json()

    except httpx.HTTPStatusError as err:
        try:
            error_data = err.response.json()
            errors_list = error_data.get("errors", [])
            error = errors_list[0] if errors_list else {}

            error_code = error.get("code", "INTERCOM_ERROR")
            error_msg = error.get("message", str(err))
        except Exception:
            error_code = "INTERCOM_ERROR"
            error_msg = err.response.text

        raise HTTPException(
            status_code=err.response.status_code,
            detail={"code": error_code, "message": error_msg},
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "SERVICE_UNAVAILABLE", "message": "Can't reach Intercom"},
        )

    except Exception as err:
        print(f"Unexpected error occurred: {str(err)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="INTERNAL_ERROR",
            message="Internal server error.",
        )
