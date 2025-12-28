"""Quick test of MCP server imports and tools"""
import asyncio
import sys
sys.path.insert(0, '.')

print("Testing MCP server imports...")

# Test MCP imports
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    print("✓ MCP imports successful")
except ImportError as e:
    print(f"✗ MCP import failed: {e}")
    sys.exit(1)

# Test tool imports
try:
    from mcp_server.tools.create_todo import create_todo
    from mcp_server.tools.list_todos import list_todos
    from mcp_server.tools.update_todo import update_todo
    from mcp_server.tools.delete_todo import delete_todo
    from mcp_server.tools.search_todos import search_todos
    print("✓ All MCP tools imported successfully")
except ImportError as e:
    print(f"✗ Tool import failed: {e}")
    sys.exit(1)

# Test tool functions exist and are async
print("\nTesting tool functions...")
assert asyncio.iscoroutinefunction(create_todo), "create_todo should be async"
assert asyncio.iscoroutinefunction(list_todos), "list_todos should be async"
assert asyncio.iscoroutinefunction(update_todo), "update_todo should be async"
assert asyncio.iscoroutinefunction(delete_todo), "delete_todo should be async"
assert asyncio.iscoroutinefunction(search_todos), "search_todos should be async"
print("✓ All tool functions are async")

# Test validation
print("\nTesting tool validation...")

# Test create_todo validation
result = asyncio.run(create_todo(user_id=0, title="Test"))
assert result["success"] == False
assert result["code"] == "VALIDATION_ERROR"
print("✓ create_todo validation works")

result = asyncio.run(create_todo(user_id=123, title=""))
assert result["success"] == False
assert result["code"] == "VALIDATION_ERROR"
print("✓ create_todo empty title validation works")

# Test delete_todo requires confirmation
result = asyncio.run(delete_todo(user_id=123, todo_id=1, confirm=False))
assert result["success"] == False
assert result["code"] == "CONFIRMATION_REQUIRED"
print("✓ delete_todo confirmation requirement works")

# Test search_todos empty query
result = asyncio.run(search_todos(user_id=123, query=""))
assert result["success"] == False
assert result["code"] == "VALIDATION_ERROR"
print("✓ search_todos empty query validation works")

print("\n" + "="*50)
print("All tests passed! MCP server is working correctly.")
print("="*50)
