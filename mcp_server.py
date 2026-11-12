"""Official SDK stdio adapter for the team's read-only tools."""
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from common import assistant
from models import SummarizeRequest

READ_ONLY = ToolAnnotations(readOnlyHint=True, openWorldHint=False)


def create_mcp():
    server = FastMCP("team-knowledge-assistant")

    @server.tool(annotations=READ_ONLY)
    def scan_risks() -> list[dict]:
        """Return graded risk alerts from the message snapshot."""
        return assistant.scan_risks(assistant.load_messages())

    @server.tool(annotations=READ_ONLY)
    def summarize_channel(channel: str = "#incidents") -> dict:
        """Summarize one channel."""
        normalized = SummarizeRequest(channel=channel).channel
        return {"channel": normalized,
                "summary": assistant.summarize_channel(assistant.load_messages(), normalized)}

    @server.tool(annotations=READ_ONLY)
    def extract_action_items() -> list[dict]:
        """Return validated tasks, owners, due dates and priorities."""
        return assistant.extract_action_items(assistant.load_messages())

    @server.tool(annotations=READ_ONLY)
    def ask_kb(question: str, k: int = 2) -> dict:
        """Answer from local documents with source references or refuse."""
        return assistant.ask_kb(question, k)

    return server


if __name__ == "__main__":
    create_mcp().run()
