"""
Integration tests for MCP tools with mocked Phase 2 backend.

Tests all 5 MCP tools with simulated backend responses.

Spec Reference: specs/api/mcp-tools.md
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import Response

from mcp_server.tools.create_todo import create_todo
from mcp_server.tools.list_todos import list_todos
from mcp_server.tools.update_todo import update_todo
from mcp_server.tools.delete_todo import delete_todo
from mcp_server.tools.search_todos import search_todos


class TestCreateTodoTool:
    """Test create_todo MCP tool."""

    @pytest.mark.asyncio
    async def test_create_todo_success(self, test_user_id: int):
        """TC-T1.1: Valid create - returns success with todo"""
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 456,
            "user_id": test_user_id,
            "title": "Buy milk",
            "status": "pending",
            "priority": "medium"
        }

        with patch("mcp_server.tools.create_todo.http_client.post", return_value=mock_response):
            result = await create_todo(test_user_id, "Buy milk")

        assert result["success"] is True
        assert result["todo"]["title"] == "Buy milk"
        assert "message" in result

    @pytest.mark.asyncio
    async def test_create_todo_empty_title(self, test_user_id: int):
        """TC-T1.2: Empty title - returns VALIDATION_ERROR"""
        result = await create_todo(test_user_id, "")

        assert result["success"] is False
        assert result["code"] == "VALIDATION_ERROR"
        assert "title" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_create_todo_with_all_fields(self, test_user_id: int):
        """TC-T1.3: With all fields - todo created with all fields"""
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 457,
            "user_id": test_user_id,
            "title": "Important task",
            "description": "Task details",
            "status": "pending",
            "priority": "high",
            "due_date": "2025-12-25T00:00:00Z"
        }

        with patch("mcp_server.tools.create_todo.http_client.post", return_value=mock_response):
            result = await create_todo(
                test_user_id,
                "Important task",
                description="Task details",
                priority="high",
                due_date="2025-12-25T00:00:00Z"
            )

        assert result["success"] is True
        assert result["todo"]["priority"] == "high"


class TestListTodosTool:
    """Test list_todos MCP tool."""

    @pytest.mark.asyncio
    async def test_list_all_pending(self, test_user_id: int, sample_todos: list):
        """TC-T2.1: List all pending - returns all pending todos"""
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "todos": sample_todos,
            "total": len(sample_todos)
        }

        with patch("mcp_server.tools.list_todos.http_client.get", return_value=mock_response):
            result = await list_todos(test_user_id)

        assert result["success"] is True
        assert len(result["todos"]) == len(sample_todos)

    @pytest.mark.asyncio
    async def test_list_with_priority_filter(self, test_user_id: int):
        """TC-T2.2: Filter by priority - correct results"""
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "todos": [{"id": 2, "priority": "high"}],
            "total": 1
        }

        with patch("mcp_server.tools.list_todos.http_client.get", return_value=mock_response):
            result = await list_todos(test_user_id, priority="high")

        assert result["success"] is True
        assert result["todos"][0]["priority"] == "high"

    @pytest.mark.asyncio
    async def test_list_empty_result(self, test_user_id: int):
        """TC-T2.4: Empty result set - returns empty array"""
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "todos": [],
            "total": 0
        }

        with patch("mcp_server.tools.list_todos.http_client.get", return_value=mock_response):
            result = await list_todos(test_user_id, status="completed")

        assert result["success"] is True
        assert result["todos"] == []
        assert result["count"] == 0


class TestUpdateTodoTool:
    """Test update_todo MCP tool."""

    @pytest.mark.asyncio
    async def test_update_single_field(self, test_user_id: int):
        """TC-T3.1: Update single field - only priority updated"""
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 456,
            "user_id": test_user_id,
            "priority": "high"
        }

        with patch("mcp_server.tools.update_todo.http_client.put", return_value=mock_response):
            result = await update_todo(test_user_id, 456, priority="high")

        assert result["success"] is True
        assert "priority" in result["changes"]

    @pytest.mark.asyncio
    async def test_update_multiple_fields(self, test_user_id: int):
        """TC-T3.2: Update multiple fields - both fields updated"""
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 456,
            "title": "New title",
            "priority": "high"
        }

        with patch("mcp_server.tools.update_todo.http_client.put", return_value=mock_response):
            result = await update_todo(test_user_id, 456, title="New title", priority="high")

        assert result["success"] is True
        assert len(result["changes"]) == 2

    @pytest.mark.asyncio
    async def test_update_no_fields(self, test_user_id: int):
        """TC-T3.4: No fields provided - returns VALIDATION_ERROR"""
        result = await update_todo(test_user_id, 456)

        assert result["success"] is False
        assert result["code"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_update_not_found(self, test_user_id: int):
        """TC-T3.3: Todo not found - returns NOT_FOUND"""
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 404

        with patch("mcp_server.tools.update_todo.http_client.put", return_value=mock_response):
            result = await update_todo(test_user_id, 99999, title="X")

        assert result["success"] is False
        assert result["code"] == "NOT_FOUND"


class TestDeleteTodoTool:
    """Test delete_todo MCP tool."""

    @pytest.mark.asyncio
    async def test_delete_without_confirmation(self, test_user_id: int):
        """TC-T4.1: Delete without confirmation - returns CONFIRMATION_REQUIRED"""
        result = await delete_todo(test_user_id, 456, confirm=False)

        assert result["success"] is False
        assert result["code"] == "CONFIRMATION_REQUIRED"

    @pytest.mark.asyncio
    async def test_delete_with_confirmation(self, test_user_id: int):
        """TC-T4.2: Delete with confirmation - succeeds"""
        # Mock GET to fetch todo details
        mock_get_response = MagicMock(spec=Response)
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            "id": 456,
            "title": "Buy milk"
        }

        # Mock DELETE
        mock_delete_response = MagicMock(spec=Response)
        mock_delete_response.status_code = 200

        with patch("mcp_server.tools.delete_todo.http_client.get", return_value=mock_get_response):
            with patch("mcp_server.tools.delete_todo.http_client.delete", return_value=mock_delete_response):
                result = await delete_todo(test_user_id, 456, confirm=True)

        assert result["success"] is True
        assert result["deleted_todo"]["title"] == "Buy milk"

    @pytest.mark.asyncio
    async def test_delete_not_found(self, test_user_id: int):
        """TC-T4.3: Todo not found - returns NOT_FOUND"""
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 404

        with patch("mcp_server.tools.delete_todo.http_client.get", return_value=mock_response):
            result = await delete_todo(test_user_id, 99999, confirm=True)

        assert result["success"] is False
        assert result["code"] == "NOT_FOUND"


class TestSearchTodosTool:
    """Test search_todos MCP tool."""

    @pytest.mark.asyncio
    async def test_search_with_results(self, test_user_id: int):
        """TC-T5.1: Search with results - returns matching todos"""
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "todos": [
                {"id": 1, "title": "Buy groceries", "relevance_score": 0.95}
            ]
        }

        with patch("mcp_server.tools.search_todos.http_client.get", return_value=mock_response):
            result = await search_todos(test_user_id, "groceries")

        assert result["success"] is True
        assert len(result["todos"]) > 0
        assert result["query"] == "groceries"

    @pytest.mark.asyncio
    async def test_search_empty_query(self, test_user_id: int):
        """TC-T5.2: Empty query - returns VALIDATION_ERROR"""
        result = await search_todos(test_user_id, "")

        assert result["success"] is False
        assert result["code"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_search_no_results(self, test_user_id: int):
        """TC-T5.3: No results - returns empty array"""
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "todos": []
        }

        with patch("mcp_server.tools.search_todos.http_client.get", return_value=mock_response):
            result = await search_todos(test_user_id, "xyzabc")

        assert result["success"] is True
        assert result["todos"] == []
        assert result["count"] == 0


class TestMCPToolsErrorHandling:
    """Test error handling across all MCP tools."""

    @pytest.mark.asyncio
    async def test_backend_timeout(self, test_user_id: int):
        """TC-2.11.1: Backend timeout - returns TIMEOUT error"""
        with patch("mcp_server.tools.list_todos.http_client.get", side_effect=TimeoutError):
            result = await list_todos(test_user_id)

        assert result["success"] is False
        assert result["code"] in ["TIMEOUT", "INTERNAL_ERROR"]

    @pytest.mark.asyncio
    async def test_backend_500_error(self, test_user_id: int):
        """TC-2.11.2: Backend 500 error - returns BACKEND_ERROR"""
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 500

        with patch("mcp_server.tools.create_todo.http_client.post", return_value=mock_response):
            result = await create_todo(test_user_id, "Test")

        assert result["success"] is False
        assert result["code"] == "BACKEND_ERROR"
