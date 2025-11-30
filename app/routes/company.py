import httpx
from fastapi import APIRouter, status, HTTPException
from configs.env import env
from app.lib.schemas import company
from datetime import datetime
from app.utils.responses import COMMON_RESPONSES

company_router = APIRouter()
INTERCOM_URL = "https://api.intercom.io/companies"
INTERCOM_HEADERS = {
    "Content-type": "application/json",
    "Intercom-Version": "2.14",
    "Authorization": f"Bearer {env.intercom_access_token}",
}


@company_router.get("/")
async def get_all_companies():
    async with httpx.AsyncClient(
        headers={
            "Content-Type": "application/json",
            "Intercom-Version": "2.14",
            "Authorization": f"Bearer {env.intercom_access_token}",
        }
    ) as client:
        response = await client.get(INTERCOM_URL)
        data = response.json()
        return data


# No response model for now
@company_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a company",
    responses=COMMON_RESPONSES,
)
async def create_company(company_data: company.CompanyCreate):
    payload = company_data.model_dump()

    current_timestamp = int(datetime.now().timestamp()) - 10000
    payload["remote_created_at"] = current_timestamp
    clean_payload = {k: v for k, v in payload.items() if v is not None}

    try:
        async with httpx.AsyncClient(headers=INTERCOM_HEADERS) as client:
            response = await client.post(INTERCOM_URL, json=clean_payload)
            response.raise_for_status()
            return {"message": "Company created successfully"}

    except httpx.HTTPStatusError as err:
        try:
            error_data: dict = err.response.json()
            errors_list = error_data.get("errors", [])
            error = errors_list[0] if errors_list else {}

            error_code = error.get("code", "INTERCOM_ERROR")
            error_msg = error.get("message", str(err))
        except Exception:
            error_code = "INTERCOM_ERROR"
            error_msg = err.response.text

        raise HTTPException(
            status_code=err.response.status_code,
            detail={"code": error_code.upper(), "message": error_msg},
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "SERVICE_UNAVAILABLE", "message": "Connection refused"},
        )

    except Exception as err:
        print(f"Unexpected error occurred: {str(err)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Internal server error"},
        )


@company_router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Update a company",
    responses=COMMON_RESPONSES,
)
async def update_company(id, company_data: company.CompanyUpdate):
    payload = company_data.model_dump()

    payload["company_id"] = id
    clean_payload = {k: v for k, v in payload.items() if v is not None}

    try:
        async with httpx.AsyncClient(headers=INTERCOM_HEADERS) as client:
            response = await client.post(INTERCOM_URL, json=clean_payload)
            response.raise_for_status()
            return {"message": f"Company {id} updated successfully"}
    except httpx.HTTPStatusError as err:
        try:
            error_data: dict = err.response.json()
            errors_list = error_data.get("errors", [])
            error = errors_list[0] if errors_list else {}

            error_code = error.get("code", "INTERCOM_ERROR")
            error_message = error.get("message", str(err))
        except Exception:
            error_code = "INTERCOM_ERROR"
            error_message = err.response.text
        raise HTTPException(
            status_code=err.response.status_code,
            detail={"code": error_code.upper(), "message": error_message},
        )
    except httpx.RequestError as err:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "SERVICE_UNAVAILABLE", "message": "Connection refused"},
        )
    except Exception as err:
        print(f"Unexpected error occurred: {str(err)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Internal server error"},
        )
