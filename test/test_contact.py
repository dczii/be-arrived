import pytest
import json
import httpx
from httpx import Response, RequestError, ASGITransport
from app.main import app
from configs.env import env
import pytest_asyncio

pytestmark = pytest.mark.asyncio

INTERCOM_URL = "https://api.intercom.io/contacts"
INTERCOM_HEADERS = {
    "Content-type": "application/json",
    "Intercom-Version": "2.14",
    "Authorization": f"Bearer {env.intercom_access_token}",
}
INTERNAL_API_URL = "/api/contacts/"


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
        await ac.aclose()


@pytest.fixture
def valid_create_contact_payload():
    return {
        "email": "dczii@live.com",
        "name": "test_user",
        "phone": "+639123456789",
        "role": "lead",
    }


@pytest.fixture
def valid_update_contact_payload():
    return {
        "name": "test_user",
        "email": "dczii@live.com",
        "phone": "",
    }


def assert_intercom_headers(actual):
    for key, value in INTERCOM_HEADERS.items():
        assert actual.headers[key] == value


def assert_error_response(response, status, code, message=None):
    json_data = response.json()
    assert response.status_code == status
    assert json_data["code"] == code
    if message:
        assert json_data["message"] == message


class TestGetAllContacts:
    async def test_success(self, respx_mock, async_client):
        mock_intercom_response = {
            "type": "list",
            "data": [],
            "total_count": 0,
            "pages": {},
        }

        respx_mock.get(INTERCOM_URL).mock(
            return_value=Response(200, json=mock_intercom_response)
        )

        response = await async_client.get(INTERNAL_API_URL)
        assert response.status_code == 200
        assert response.json() == mock_intercom_response

        actual_request = respx_mock.calls.last.request
        assert_intercom_headers(actual_request)

    async def test_http_status_error(self, respx_mock, async_client):
        error_response = {
            "errors": [{"code": "UNAUTHORIZED", "message": "Access Token Invalid"}]
        }

        respx_mock.get(INTERCOM_URL).mock(
            return_value=Response(401, json=error_response)
        )

        response = await async_client.get(INTERNAL_API_URL)
        assert_error_response(response, 401, "UNAUTHORIZED", "Access Token Invalid")

    async def test_unexpected_error(self, respx_mock, async_client):
        respx_mock.get(INTERCOM_URL).mock(side_effect=Exception("error"))

        response = await async_client.get(INTERNAL_API_URL)
        assert_error_response(response, 500, "INTERNAL_ERROR", "Internal server error")

    
    async def test_network_error(self, respx_mock, async_client):
        respx_mock.get(INTERCOM_URL).mock(
            side_effect=RequestError("Connection refused")
        )

        response = await async_client.get(INTERNAL_API_URL)
        assert_error_response(
            response, 503, "SERVICE_UNAVAILABLE", "Connection refused"
        )

class TestCreateContact:

    
    async def test_success(
        self, respx_mock, async_client, valid_create_contact_payload
    ):
        mock_response_data = {"message": "Contact created successfully"}

        respx_mock.post(INTERCOM_URL).mock(
            return_value=Response(201, json=mock_response_data)
        )

        response = await async_client.post(
            INTERNAL_API_URL, json=valid_create_contact_payload
        )
        assert response.status_code == 201
        assert response.json() == mock_response_data

        actual = respx_mock.calls.last.request
        sent_payload = json.loads(actual.content)
        assert isinstance(sent_payload["signed_up_at"], int)
        assert isinstance(sent_payload["last_seen_at"], int)

    
    async def test_http_status_error(
        self, respx_mock, async_client, valid_create_contact_payload
    ):
        error_response = {
            "errors": [{"code": "UNAUTHORIZED", "message": "Access Token Invalid"}]
        }

        respx_mock.post(INTERCOM_URL).mock(
            return_value=Response(401, json=error_response)
        )

        response = await async_client.post(
            INTERNAL_API_URL, json=valid_create_contact_payload
        )
        assert_error_response(response, 401, "UNAUTHORIZED")

    
    async def test_validation_error(self, respx_mock, async_client):
        error_response = {
            "errors": [{"code": "VALIDATION_ERROR", "message": "Email required"}]
        }

        respx_mock.post(INTERCOM_URL).mock(
            return_value=Response(422, json=error_response)
        )

        response = await async_client.post(INTERNAL_API_URL, json={})
        assert_error_response(response, 422, "VALIDATION_ERROR")

    
    async def test_network_error(
        self, respx_mock, async_client, valid_create_contact_payload
    ):
        respx_mock.post(INTERCOM_URL).mock(
            side_effect=RequestError("Connection refused")
        )

        response = await async_client.post(
            INTERNAL_API_URL, json=valid_create_contact_payload
        )
        assert_error_response(
            response, 503, "SERVICE_UNAVAILABLE", "Connection refused"
        )

    
    async def test_unexpected_error(
        self, respx_mock, async_client, valid_create_contact_payload
    ):
        respx_mock.post(INTERCOM_URL).mock(side_effect=Exception("Unexpected error"))

        response = await async_client.post(
            INTERNAL_API_URL, json=valid_create_contact_payload
        )
        assert_error_response(response, 500, "INTERNAL_ERROR", "Internal server error")

class TestUpdateContact:
    CONTACT_ID = "63a07ddf05a32042dffac965"
    INTERNAL_URL = f"/api/contacts/{CONTACT_ID}"
    EXTERNAL_URL = f"{INTERCOM_URL}/{CONTACT_ID}"

    
    async def test_success(
        self, respx_mock, async_client, valid_update_contact_payload
    ):
        mock_response_data = {"message": f"User {self.CONTACT_ID} updated successfully"}

        respx_mock.put(self.EXTERNAL_URL).mock(
            return_value=Response(200, json=mock_response_data)
        )

        response = await async_client.put(
            self.INTERNAL_URL, json=valid_update_contact_payload
        )
        assert response.status_code == 200
        assert response.json() == mock_response_data

        actual = respx_mock.calls.last.request
        sent_payload = json.loads(actual.content)
        assert isinstance(sent_payload["updated_at"], int)
        assert isinstance(sent_payload["last_seen_at"], int)

    
    async def test_http_status_error(
        self, respx_mock, async_client, valid_update_contact_payload
    ):
        error_response = {
            "errors": [{"code": "UNAUTHORIZED", "message": "Access Token Invalid"}]
        }

        respx_mock.put(self.EXTERNAL_URL).mock(
            return_value=Response(401, json=error_response)
        )

        response = await async_client.put(
            self.INTERNAL_URL, json=valid_update_contact_payload
        )
        assert_error_response(response, 401, "UNAUTHORIZED")

    
    async def test_validation_error(self, respx_mock, async_client):
        error_response = {
            "errors": [{"code": "VALIDATION_ERROR", "message": "Email required"}]
        }

        respx_mock.put(self.EXTERNAL_URL).mock(
            return_value=Response(422, json=error_response)
        )

        response = await async_client.put(self.INTERNAL_URL, json={})
        assert_error_response(response, 422, "VALIDATION_ERROR")

    
    async def test_network_error(
        self, respx_mock, async_client, valid_update_contact_payload
    ):
        respx_mock.put(self.EXTERNAL_URL).mock(
            side_effect=RequestError("Connection refused")
        )

        response = await async_client.put(
            self.INTERNAL_URL, json=valid_update_contact_payload
        )
        assert_error_response(
            response, 503, "SERVICE_UNAVAILABLE", "Connection refused"
        )

    
    async def test_unexpected_error(
        self, respx_mock, async_client, valid_update_contact_payload
    ):
        respx_mock.put(self.EXTERNAL_URL).mock(
            side_effect=Exception("Unexpected error")
        )

        response = await async_client.put(
            self.INTERNAL_URL, json=valid_update_contact_payload
        )
        assert_error_response(response, 500, "INTERNAL_ERROR", "Internal server error")
