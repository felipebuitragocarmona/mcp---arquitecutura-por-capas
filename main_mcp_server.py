import os
from dotenv import load_dotenv
from presentation.mcp.tools import mcp

load_dotenv()

PORT = int(os.getenv("MCP_PORT", 9000))

print("=" * 40)
print("Starting MCP Server...")
print(f"MCP_PORT loaded: {PORT}")
print("Transport: SSE")
print("=" * 40)

mcp.run(transport="sse", port=PORT)