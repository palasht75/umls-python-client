import unittest
from unittest.mock import Mock

import requests

from umls_python_client.baseAPI.umls_api_base import UMLSAPIBase


class DummyAPI(UMLSAPIBase):
    pass


def _mock_response(status_code=200, json_payload=None, text=""):
    response = Mock()
    response.status_code = status_code
    response.text = text
    if json_payload is None:
        response.json.side_effect = ValueError("invalid json")
    else:
        response.json.return_value = json_payload
    return response


class TestBaseAPI(unittest.TestCase):
    def test_rejects_empty_api_key(self):
        with self.assertRaises(ValueError):
            DummyAPI("")

    def test_request_includes_api_key_and_timeout(self):
        session = Mock()
        session.get.return_value = _mock_response(json_payload={"result": []})
        api = DummyAPI("k", session=session, timeout=12.5)

        payload = api._request(path="/search/current", params={"string": "diabetes"})

        self.assertEqual(payload, {"result": []})
        session.get.assert_called_once()
        _, kwargs = session.get.call_args
        self.assertEqual(kwargs["params"]["apiKey"], "k")
        self.assertEqual(kwargs["params"]["string"], "diabetes")
        self.assertEqual(kwargs["timeout"], 12.5)

    def test_request_handles_network_error(self):
        session = Mock()
        session.get.side_effect = requests.RequestException("network down")
        api = DummyAPI("k", session=session)

        payload = api._request(path="/search/current")

        self.assertEqual(payload["error"], "Request failed.")
        self.assertIn("network down", payload["message"])

    def test_handle_response_for_unauthorized(self):
        api = DummyAPI("k")
        payload = api._handle_response(_mock_response(status_code=401, text="nope"))
        self.assertEqual(payload["status_code"], 401)
        self.assertIn("Invalid API Key", payload["error"])


if __name__ == "__main__":
    unittest.main()
