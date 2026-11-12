import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ["APP_MODE"] = "offline"
from common import assistant, llm, nlp
from common.retriever import TfidfIndex
from models import Digest

def message(**changes):
    return dict({"id": "m1", "sim_ts": "2027-07-13T08:00:00", "author": "alex",
                 "channel": "#engineering", "text": "All services normal."}, **changes)

class BusinessTests(unittest.TestCase):
    def test_snapshot_and_pipeline_contract(self):
        data = assistant.load_messages()
        self.assertGreater(len(data), 0)
        result = assistant.run_pipeline(data, ["Are webhooks signed?"])
        Digest.model_validate(result)
        self.assertEqual(result["message_count"], len(data))
        self.assertTrue(result["tasks"])
        self.assertTrue(result["faq"][0]["sources"])

    def test_invalid_input_and_duplicate_id(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "data.jsonl"
            for rows in ([{}], [message(author=12)], [message(sim_ts="invalid")],
                         [message(), message()]):
                path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "line"):
                    assistant.load_messages(path)

    def test_summary_empty_channel(self):
        self.assertEqual(assistant.summarize_channel([message()], "#missing"), "No messages in this channel.")
        self.assertIn("Offline", assistant.summarize_channel([message()], "#engineering"))

    def test_task_year_comes_from_source(self):
        tasks = nlp.extract_tasks([message(text="1. Alex - Update runbook. Due 7/15")])
        self.assertEqual(tasks, [{"task": "Update runbook", "owner": "alex",
                                 "due": "2027-07-15", "priority": "high"}])

    def test_invalid_model_output_fails(self):
        for raw in ("not JSON", '[{"task":"Fix","priority":"urgent"}]',
                    '[{"task":"Fix","priority":"high","due":"2027-02-30"}]'):
            with self.subTest(raw=raw), patch.object(nlp, "call_llm", return_value=raw):
                with self.assertRaises(ValueError):
                    nlp.extract_tasks([message()])

    def test_risk_precedence_and_skip(self):
        alerts = assistant.scan_risks([message(text="outage blocked"),
                                      message(id="m2", text="outage", channel="#random"), message(id="m3")])
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["severity"], "high")
        self.assertEqual(alerts[0]["message_id"], "m1")

    def test_citations_and_refusal(self):
        answer = assistant.ask_kb("Are webhooks signed?")
        self.assertFalse(answer["refused"])
        self.assertTrue(all("#" in source for source in answer["sources"]))
        self.assertTrue(assistant.ask_kb("What is the capital of France?")["refused"])
        self.assertTrue(assistant.ask_kb("Are webhooks signed?", index=TfidfIndex())["refused"])

    def test_index_cache_key_is_directory(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            (Path(first) / "one.md").write_text("Webhook signing with HMAC.", encoding="utf-8")
            (Path(second) / "two.md").write_text("Payment retry policy.", encoding="utf-8")
            a, b = assistant.kb_index(first), assistant.kb_index(second)
            self.assertIsNot(a, b)
            self.assertEqual(a.docs[0]["meta"]["source"], "one.md")
            self.assertEqual(b.docs[0]["meta"]["source"], "two.md")

    def test_offline_with_key(self):
        with patch.dict(os.environ, {"APP_MODE": "offline", "OPENAI_API_KEY": "unused"}):
            self.assertEqual(llm.call_llm("s", "u", mock="excerpt"), "excerpt")
        with patch.dict(os.environ, {"APP_MODE": "live"}, clear=True):
            with self.assertRaises(llm.ConfigurationError):
                llm.llm_provider()

if __name__ == "__main__":
    unittest.main()
