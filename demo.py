"""Generate a reproducible offline digest."""
import json
import os
from pathlib import Path

os.environ["APP_MODE"] = "offline"
from common.assistant import run_pipeline

def main():
    result = run_pipeline(faq_queries=["Are webhooks signed?", "What is the capital of France?"])
    output = Path(__file__).resolve().parent / "outputs" / "digest.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"Saved {output.name}")

if __name__ == "__main__":
    main()
