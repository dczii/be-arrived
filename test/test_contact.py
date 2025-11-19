import pytest
import json
from fastapi.testclient import TestClient
from httpx import Response, RequestError
from app.main import app
from configs import env


client = TestClient(app)

INTERCOM_URL = "https://api.intercom.io/contacts"
INTERCOM_HEADERS = {
    "Content-type": "application/json",
    "Intercom-Version": "2.14",
    "Authorization": f"Bearer {env.intercom_access_token}",
}

INTERNAL_API_URL = "/api/contacts"


@pytest.fixture
def valid_payload():
    return {
        "email": "dczii@live.com",
        "name": "test_user",
        "phone": "+639123456789",
        "role": "lead"
    }


class TestGetAllContacts:
    @pytest.mark.asyncio
    async def test_success(self, respx_mock):
        mock_intercom_response = {
            "type": "list",
            "data": [],
            "total_count": 0,
            "pages": {},
        }

        # Mock intercom api
        respx_mock.get(INTERCOM_URL, headers=INTERCOM_HEADERS).mock(
            return_value=Response(200, json=mock_intercom_response)
        )

        response = client.get(INTERNAL_API_URL)

        assert response.status_code == 200
        assert response.json() == mock_intercom_response

        actual_request = respx_mock.calls.last.request
        assert (
            actual_request.headers["Content-type"] == INTERCOM_HEADERS["Content-type"]
        )
        assert (
            actual_request.headers["Intercom-Version"]
            == INTERCOM_HEADERS["Intercom-Version"]
        )
        assert (
            actual_request.headers["Authorization"] == INTERCOM_HEADERS["Authorization"]
        )

    @pytest.mark.asyncio
    async def test_http_status_error(self, respx_mock):
        # Mock intercom error response
        error_response = {
            "errors": [{"code": "UNAUTHORIZED", "message": "Access Token Invalid"}]
        }

        respx_mock.get(INTERCOM_URL, headers=INTERCOM_HEADERS).mock(
            return_value=Response(401, json=error_response)
        )

        response = client.get(INTERNAL_API_URL)

        assert response.status_code == 401
        assert response.json()["message"] == "Access Token Invalid"
        assert response.json()["code"] == "UNAUTHORIZED"

    @pytest.mark.asyncio
    async def test_unexpected_error(self, respx_mock):
        # Mock exeption
        respx_mock.get(INTERCOM_URL, headers=INTERCOM_HEADERS).mock(
            side_effect=Exception("error")
        )

        response = client.get(INTERNAL_API_URL)

        assert response.status_code == 500
        data = response.json()
        assert data["code"] == "INTERNAL_ERROR"
        assert data["message"] == "Internal server error"

    @pytest.mark.asyncio
    async def test_network_error(self, respx_mock):
        # Mock network error
        respx_mock.get(INTERCOM_URL, headers=INTERCOM_HEADERS).mock(
            side_effect=RequestError("Connection refused")
        )

        response = client.get(INTERNAL_API_URL)

        assert response.status_code == 503
        assert response.json()["code"] == "SERVICE_UNAVAILABLE"
        assert response.json()["message"] == "Connection refused"


class TestCreateContact:
    @pytest.mark.asyncio
    async def test_success(self, respx_mock, valid_payload):
        mock_response_data = {"message": "Contact created successfully"}

        # Mock intercom api
        respx_mock.post(INTERCOM_URL, headers=INTERCOM_HEADERS).mock(
            return_value=Response(201, json=mock_response_data)
        )

        response = client.post(INTERNAL_API_URL, json=valid_payload)
        assert response.status_code == 201
        assert response.json() == mock_response_data

        actual_request = respx_mock.calls.last.request
        sent_payload = json.loads(actual_request.content)
        assert isinstance(sent_payload["signed_up_at"], int)
        assert isinstance(sent_payload["last_seen_at"], int)

    @pytest.mark.asyncio
    async def test_validation_error(self, respx_mock, valid_payload):
        # Mock Intercom error response
        error_response = {
            "errors": [
                {"code": "VALIDATION_ERROR", "message": "Email has already been taken"}
            ]
        }

        respx_mock.post(INTERCOM_URL, headers=INTERCOM_HEADERS).mock(
            return_value=Response(422, json=error_response)
        )

        response = client.post(INTERNAL_API_URL, json=valid_payload)
        assert response.status_code == 422
        assert response.json()["code"] == "VALIDATION_ERROR"
        assert response.json()["message"] == "Email has already been taken"

    @pytest.mark.asyncio
    async def test_network_error(self, respx_mock, valid_payload):
        respx_mock.post(INTERCOM_URL, headers=INTERCOM_HEADERS).mock(
            side_effect=RequestError("Connection refused")
        )

        response = client.post(INTERNAL_API_URL, json=valid_payload)

        assert response.status_code == 503
        assert response.json()["code"] == "SERVICE_UNAVAILABLE"
        assert response.json()["message"] == "Connection refused"

    @pytest.mark.asyncio
    async def test_unexpected_crash(self, respx_mock, valid_payload):
        respx_mock.post(INTERCOM_URL).mock(side_effect=Exception("Unexpected error"))

        response = client.post(INTERNAL_API_URL, json=valid_payload)

        assert response.status_code == 500
        assert response.json()["code"] == "INTERNAL_ERROR"
        assert response.json()["message"] == "Internal server error"
