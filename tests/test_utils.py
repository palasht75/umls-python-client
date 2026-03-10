import json
import unittest

from umls_python_client.utils.utils import handle_response_with_format


class TestUtils(unittest.TestCase):
    def test_json_response_indented(self):
        output = handle_response_with_format({"result": {"name": "x"}}, format="json")
        self.assertIsInstance(output, str)
        self.assertIn('"name": "x"', output)

    def test_json_response_raw(self):
        payload = {"result": [1, 2]}
        output = handle_response_with_format(
            payload, format="json", return_indented=False
        )
        self.assertEqual(output, payload)

    def test_rdf_falls_back_when_payload_not_convertible(self):
        output = handle_response_with_format("not-json", format="rdf")
        parsed = json.loads(output)
        self.assertEqual(parsed, "not-json")

    def test_invalid_format_raises_value_error(self):
        with self.assertRaises(ValueError):
            handle_response_with_format({"result": []}, format="xml")


if __name__ == "__main__":
    unittest.main()
