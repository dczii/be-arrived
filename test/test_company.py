import pytest
import json
import httpx
from httpx import Response, RequestError, ASGITransport
from app.main import app
from configs.env import env
import pytest_asyncio

pytestmark = pytest.mark.asyncio

INTERCOM_URL = "https://api.intercom.io/companies"
INTERCOM_HEADERS = {
    "Content-type": "application/json",
    "Intercom-Version": "2.14",
    "Authorization": f"Bearer {env.intercom_access_token}",
}
INTERNAL_API_URL = "/api/companies/"


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
        await ac.aclose()


@pytest.fixture
def valid_create_company_payload():
    return {
        "company_id": "105",
        "name": "test company",
        "size": 50,
        "industry": "Tech",
        "monthly_spend": 200,
    }


@pytest.fixture
def valid_update_company_payload():
    return {
        "name": "Acme Corp Updated",
        "plan": "enterprise",
        "size": 100,
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


class TestCreateCompany:
    async def test_success(
        self, respx_mock, async_client, valid_create_company_payload
    ):
        mock_response_data = {"message": "Company created successfully"}

        respx_mock.post(INTERCOM_URL).mock(
            return_value=Response(201, json=mock_response_data)
        )

        response = await async_client.post(
            INTERNAL_API_URL, json=valid_create_company_payload
        )
        assert response.status_code == 201
        assert response.json() == mock_response_data

        actual = respx_mock.calls.last.request
        sent_payload = json.loads(actual.content)
        assert "website" not in sent_payload

    async def test_http_status_error(
        self, respx_mock, async_client, valid_create_company_payload
    ):
        error_response = {
            "errors": [{"code": "UNAUTHORIZED", "message": "Access Token Invalid"}]
        }

        respx_mock.post(INTERCOM_URL).mock(
            return_value=Response(401, json=error_response)
        )

        response = await async_client.post(
            INTERNAL_API_URL, json=valid_create_company_payload
        )
        assert_error_response(response, 401, "UNAUTHORIZED")

    async def test_validation_error(self, respx_mock, async_client):
        response = await async_client.post(INTERNAL_API_URL, json={})
        assert_error_response(response, 422, "VALIDATION_ERROR")

    async def test_network_error(
        self, respx_mock, async_client, valid_create_company_payload
    ):
        respx_mock.post(INTERCOM_URL).mock(
            side_effect=RequestError("Connection refused")
        )

        response = await async_client.post(
            INTERNAL_API_URL, json=valid_create_company_payload
        )
        assert_error_response(
            response, 503, "SERVICE_UNAVAILABLE", "Connection refused"
        )

    async def test_unexpected_error(
        self, respx_mock, async_client, valid_create_company_payload
    ):
        respx_mock.post(INTERCOM_URL).mock(side_effect=Exception("Unexpected error"))

        response = await async_client.post(
            INTERNAL_API_URL, json=valid_create_company_payload
        )
        assert_error_response(response, 500, "INTERNAL_ERROR", "Internal server error")


class TestUpdateCompany:
    COMPANY_ID = "105"
    INTERNAL_URL = f"/api/companies/{COMPANY_ID}"
    EXTERNAL_URL = INTERCOM_URL

    async def test_success(
        self, respx_mock, async_client, valid_update_company_payload
    ):
        mock_response_data = {
            "message": f"Company {self.COMPANY_ID} updated successfully"
        }

        respx_mock.post(self.EXTERNAL_URL).mock(
            return_value=Response(200, json=mock_response_data)
        )

        response = await async_client.put(
            self.INTERNAL_URL, json=valid_update_company_payload
        )
        assert response.status_code == 200
        assert response.json() == mock_response_data

        actual = respx_mock.calls.last.request
        sent_payload = json.loads(actual.content)

        assert sent_payload["company_id"] == self.COMPANY_ID
        assert "website" not in sent_payload
        assert "remote_created_at" not in sent_payload
        assert "last_request_at" not in sent_payload

    async def test_http_status_error(
        self, respx_mock, async_client, valid_update_company_payload
    ):
        error_response = {
            "errors": [{"code": "UNAUTHORIZED", "message": "Access Token Invalid"}]
        }

        respx_mock.post(self.EXTERNAL_URL).mock(
            return_value=Response(401, json=error_response)
        )

        response = await async_client.put(
            self.INTERNAL_URL, json=valid_update_company_payload
        )
        assert_error_response(response, 401, "UNAUTHORIZED")

    async def test_validation_error(self, respx_mock, async_client):
        response = await async_client.put(
            self.INTERNAL_URL, json={"size": "invalid_number"}
        )
        assert response.status_code == 422

    async def test_network_error(
        self, respx_mock, async_client, valid_update_company_payload
    ):
        respx_mock.post(self.EXTERNAL_URL).mock(
            side_effect=RequestError("Connection refused")
        )

        response = await async_client.put(
            self.INTERNAL_URL, json=valid_update_company_payload
        )
        assert_error_response(
            response, 503, "SERVICE_UNAVAILABLE", "Connection refused"
        )

    async def test_unexpected_error(
        self, respx_mock, async_client, valid_update_company_payload
    ):
        respx_mock.post(self.EXTERNAL_URL).mock(
            side_effect=Exception("Unexpected error")
        )

        response = await async_client.put(
            self.INTERNAL_URL, json=valid_update_company_payload
        )
        assert_error_response(response, 500, "INTERNAL_ERROR", "Internal server error")
