import os
import unittest
from unittest.mock import patch

os.environ["APP_MODE"] = "offline"
from fastapi.testclient import TestClient
from api import app
from common import assistant

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"APP_MODE": "offline", "SERVICE_API_KEY": ""})
        self.env.start()
        self.client = TestClient(app)
    def tearDown(self):
        self.client.close()
        self.env.stop()

    def test_health_readiness(self):
        self.assertEqual(self.client.get("/healthz").status_code, 200)
        self.assertGreater(self.client.get("/readyz").json()["kb_chunks"], 0)
        with patch.object(assistant, "load_messages", side_effect=ValueError("private payload")):
            response = self.client.get("/readyz")
            self.assertEqual(response.status_code, 503)
            self.assertNotIn("private payload", response.text)

    def test_request_validation(self):
        for body in ({"question": " "}, {"question": "webhooks", "k": 0},
                     {"question": "webhooks", "k": 6}, {"question": "x"*2001}):
            self.assertEqual(self.client.post("/ask", json=body).status_code, 422)
        self.assertEqual(self.client.post("/digest", json={"faq_queries": ["webhooks"]*11}).status_code, 422)
        self.assertEqual(self.client.post("/summarize", json={"channel": "  "}).status_code, 422)

    def test_digest_matches_individual_capabilities(self):
        result = self.client.post("/digest", json={"faq_queries": ["Are webhooks signed?"]})
        self.assertEqual(result.status_code, 200)
        data = result.json()
        self.assertEqual(data["alerts"], self.client.get("/alerts").json()["alerts"])
        self.assertEqual(data["tasks"], self.client.get("/tasks").json()["tasks"])
        summary = self.client.post("/summarize", json={"channel": "incidents"}).json()
        self.assertEqual(data["summaries"]["#incidents"], summary["summary"])
        self.assertEqual(data["faq"][0], self.client.post("/ask", json={"question": "Are webhooks signed?"}).json())

    def test_token_auth(self):
        with patch.dict(os.environ, {"SERVICE_API_KEY": "test-token"}):
            self.assertEqual(self.client.get("/healthz").status_code, 200)
            self.assertEqual(self.client.get("/readyz").status_code, 401)
            self.assertEqual(self.client.get("/readyz", headers={"Authorization": "Bearer test-token"}).status_code, 200)

    def test_model_error_not_success_or_payload_leak(self):
        with patch.object(assistant, "extract_action_items", side_effect=ValueError("private provider body")):
            response = self.client.get("/tasks")
            self.assertEqual(response.status_code, 502)
            self.assertNotIn("private provider body", response.text)
