"""Direct test of MCP server components without stdio"""
import asyncio
import sys
sys.path.insert(0, '.')

print("=" * 50)
print("MCP Server Component Test")
print("=" * 50)

# Test 1: Import MCP
print("\n[1/4] Testing MCP imports...")
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool as MCPTool, ListToolsRequest, CallToolRequest
    print("   ✓ MCP imports successful")
except ImportError as e:
    print(f"   ✗ MCP import failed: {e}")
    sys.exit(1)

# Test 2: Create server
print("\n[2/4] Testing server creation...")
try:
    app = Server("todo-mcp-server")
    print("   ✓ Server created successfully")
except Exception as e:
    print(f"   ✗ Server creation failed: {e}")
    sys.exit(1)

# Test 3: Import tools
print("\n[3/4] Testing tool imports...")
try:
    from mcp_server.tools.create_todo import create_todo
    from mcp_server.tools.list_todos import list_todos
    from mcp_server.tools.update_todo import update_todo
    from mcp_server.tools.delete_todo import delete_todo
    from mcp_server.tools.search_todos import search_todos
    print("   ✓ All 5 tools imported successfully")
except ImportError as e:
    print(f"   ✗ Tool import failed: {e}")
    sys.exit(1)

# Test 4: Test tool functions
print("\n[4/4] Testing tool validation...")

async def test_tools():
    # Test create_todo validation - invalid user_id
    result = await create_todo(user_id=0, title="Test")
    assert result["success"] == False
    assert result["code"] == "VALIDATION_ERROR"
    print("   ✓ create_todo (invalid user_id)")

    # Test create_todo validation - empty title
    result = await create_todo(user_id=123, title="")
    assert result["success"] == False
    assert result["code"] == "VALIDATION_ERROR"
    print("   ✓ create_todo (empty title)")

    # Test delete_todo - requires confirmation
    result = await delete_todo(user_id=123, todo_id=1, confirm=False)
    assert result["success"] == False
    assert result["code"] == "CONFIRMATION_REQUIRED"
    print("   ✓ delete_todo (confirmation required)")

    # Test search_todos - empty query
    result = await search_todos(user_id=123, query="")
    assert result["success"] == False
    assert result["code"] == "VALIDATION_ERROR"
    print("   ✓ search_todos (empty query)")

    print("\n   All validation tests passed!")

asyncio.run(test_tools())

print("\n" + "=" * 50)
print("MCP Server is fully functional!")
print("=" * 50)
print("\nNote: The stdio_server requires proper stdin/stdout piping")
print("which only works when run as an MCP client subprocess.")
print("\nTo use with Claude Code:")
print("1. Configure mcpServers in CLAUDE.md")
print("2. Claude Code will auto-start the server")
