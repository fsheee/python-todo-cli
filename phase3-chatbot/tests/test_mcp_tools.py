"""
Unit Tests for MCP Tools

Tests for mcp_server/tools/*.py

Spec Reference: specs/api/mcp-tools.md - Testing Strategy
Task: 2.12
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_client():
    """Create mock HTTP client"""
    client = AsyncMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.put = AsyncMock()
    client.delete = AsyncMock()
    client.close = AsyncMock()
    return client


class TestCreateTodo:
    """Tests for create_todo MCP tool"""

    @pytest.mark.asyncio
    async def test_create_todo_success(self, mock_client):
        """Test successful todo creation"""
        from mcp_server.tools.create_todo import create_todo

        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 1,
            "user_id": 123,
            "title": "Buy groceries",
            "status": "pending"
        }
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch('mcp_server.tools.create_todo.get_client', return_value=mock_client):
            result = await create_todo(
                user_id=123,
                title="Buy groceries"
            )

        assert result["success"] is True
        assert result["todo"]["title"] == "Buy groceries"

    @pytest.mark.asyncio
    async def test_create_todo_invalid_user_id(self):
        """Test todo creation with invalid user_id"""
        from mcp_server.tools.create_todo import create_todo

        result = await create_todo(
            user_id=0,
            title="Buy groceries"
        )

        assert result["success"] is False
        assert result["code"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_create_todo_empty_title(self):
        """Test todo creation with empty title"""
        from mcp_server.tools.create_todo import create_todo

        result = await create_todo(
            user_id=123,
            title=""
        )

        assert result["success"] is False
        assert result["code"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_create_todo_title_too_long(self):
        """Test todo creation with title exceeding max length"""
        from mcp_server.tools.create_todo import create_todo

        long_title = "x" * 201

        result = await create_todo(
            user_id=123,
            title=long_title
        )

        assert result["success"] is False
        assert result["code"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_create_todo_invalid_priority(self):
        """Test todo creation with invalid priority"""
        from mcp_server.tools.create_todo import create_todo

        result = await create_todo(
            user_id=123,
            title="Buy groceries",
            priority="invalid"
        )

        assert result["success"] is False
        assert result["code"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_create_todo_with_all_fields(self, mock_client):
        """Test todo creation with all optional fields"""
        from mcp_server.tools.create_todo import create_todo

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 1,
            "user_id": 123,
            "title": "Finish report",
            "description": "Complete Q4 analysis",
            "priority": "high",
            "status": "pending"
        }
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch('mcp_server.tools.create_todo.get_client', return_value=mock_client):
            result = await create_todo(
                user_id=123,
                title="Finish report",
                description="Complete Q4 analysis",
                priority="high",
                due_date="2025-12-31T00:00:00Z"
            )

        assert result["success"] is True
        assert result["todo"]["priority"] == "high"


class TestListTodos:
    """Tests for list_todos MCP tool"""

    @pytest.mark.asyncio
    async def test_list_todos_success(self, mock_client):
        """Test successful todo listing"""
        from mcp_server.tools.list_todos import list_todos

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "todos": [
                {"id": 1, "title": "Buy groceries", "status": "pending"},
                {"id": 2, "title": "Call mom", "status": "pending"}
            ],
            "total": 2
        }
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch('mcp_server.tools.list_todos.get_client', return_value=mock_client):
            result = await list_todos(user_id=123)

        assert result["success"] is True
        assert len(result["todos"]) == 2

    @pytest.mark.asyncio
    async def test_list_todos_with_filters(self, mock_client):
        """Test todo listing with filters"""
        from mcp_server.tools.list_todos import list_todos

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "todos": [{"id": 1, "title": "Buy groceries", "priority": "high"}],
            "total": 1
        }
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch('mcp_server.tools.list_todos.get_client', return_value=mock_client):
            result = await list_todos(
                user_id=123,
                status="pending",
                priority="high"
            )

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_list_todos_empty(self, mock_client):
        """Test listing todos when none exist"""
        from mcp_server.tools.list_todos import list_todos

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "todos": [],
            "total": 0
        }
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch('mcp_server.tools.list_todos.get_client', return_value=mock_client):
            result = await list_todos(user_id=123)

        assert result["success"] is True
        assert len(result["todos"]) == 0


class TestUpdateTodo:
    """Tests for update_todo MCP tool"""

    @pytest.mark.asyncio
    async def test_update_todo_success(self, mock_client):
        """Test successful todo update"""
        from mcp_server.tools.update_todo import update_todo

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1,
            "title": "Buy groceries",
            "priority": "high"
        }
        mock_client.put = AsyncMock(return_value=mock_response)

        with patch('mcp_server.tools.update_todo.get_client', return_value=mock_client):
            result = await update_todo(
                user_id=123,
                todo_id=1,
                priority="high"
            )

        assert result["success"] is True
        assert result["todo"]["priority"] == "high"

    @pytest.mark.asyncio
    async def test_update_todo_not_found(self, mock_client):
        """Test updating non-existent todo"""
        from mcp_server.tools.update_todo import update_todo

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_client.put = AsyncMock(return_value=mock_response)

        with patch('mcp_server.tools.update_todo.get_client', return_value=mock_client):
            result = await update_todo(
                user_id=123,
                todo_id=999,
                title="New title"
            )

        assert result["success"] is False
        assert result["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_update_todo_no_changes(self):
        """Test updating todo with no changes specified"""
        from mcp_server.tools.update_todo import update_todo

        result = await update_todo(
            user_id=123,
            todo_id=1
        )

        assert result["success"] is False
        assert result["code"] == "VALIDATION_ERROR"


class TestDeleteTodo:
    """Tests for delete_todo MCP tool"""

    @pytest.mark.asyncio
    async def test_delete_todo_requires_confirmation(self):
        """Test that delete requires explicit confirmation"""
        from mcp_server.tools.delete_todo import delete_todo

        result = await delete_todo(
            user_id=123,
            todo_id=1,
            confirm=False
        )

        assert result["success"] is False
        assert result["code"] == "CONFIRMATION_REQUIRED"

    @pytest.mark.asyncio
    async def test_delete_todo_not_found(self, mock_client):
        """Test deleting non-existent todo"""
        from mcp_server.tools.delete_todo import delete_todo

        # Mock get response (not found)
        get_response = MagicMock()
        get_response.status_code = 404
        mock_client.get = AsyncMock(return_value=get_response)

        with patch('mcp_server.tools.delete_todo.get_client', return_value=mock_client):
            result = await delete_todo(
                user_id=123,
                todo_id=999,
                confirm=True
            )

        assert result["success"] is False
        assert result["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_delete_todo_success(self, mock_client):
        """Test successful todo deletion"""
        from mcp_server.tools.delete_todo import delete_todo

        # Mock get response (found)
        get_response = MagicMock()
        get_response.status_code = 200
        get_response.json.return_value = {
            "id": 1,
            "title": "Buy groceries"
        }
        mock_client.get = AsyncMock(return_value=get_response)

        # Mock delete response (success)
        delete_response = MagicMock()
        delete_response.status_code = 200
        mock_client.delete = AsyncMock(return_value=delete_response)

        with patch('mcp_server.tools.delete_todo.get_client', return_value=mock_client):
            result = await delete_todo(
                user_id=123,
                todo_id=1,
                confirm=True
            )

        assert result["success"] is True
        assert "Buy groceries" in result["message"] or result["deleted_todo"]["id"] == 1


class TestSearchTodos:
    """Tests for search_todos MCP tool"""

    @pytest.mark.asyncio
    async def test_search_todos_success(self, mock_client):
        """Test successful todo search"""
        from mcp_server.tools.search_todos import search_todos

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "todos": [
                {"id": 1, "title": "Buy groceries"},
                {"id": 2, "title": "Grocery shopping"}
            ]
        }
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch('mcp_server.tools.search_todos.get_client', return_value=mock_client):
            result = await search_todos(
                user_id=123,
                query="groceries"
            )

        assert result["success"] is True
        assert result["query"] == "groceries"

    @pytest.mark.asyncio
    async def test_search_todos_empty_query(self):
        """Test search with empty query"""
        from mcp_server.tools.search_todos import search_todos

        result = await search_todos(
            user_id=123,
            query=""
        )

        assert result["success"] is False
        assert result["code"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_search_todos_no_matches(self, mock_client):
        """Test search with no matching results"""
        from mcp_server.tools.search_todos import search_todos

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "todos": []
        }
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch('mcp_server.tools.search_todos.get_client', return_value=mock_client):
            result = await search_todos(
                user_id=123,
                query="xyznonexistent"
            )

        assert result["success"] is True
        assert len(result["todos"]) == 0


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
