"""Tests for Task CRUD API endpoints.

Tests per /specs/features/task-crud.md acceptance criteria.
"""

import pytest
from uuid import UUID, uuid4

# Test user ID - must match conftest.py
TEST_USER_ID = UUID("550e8400-e29b-41d4-a716-446655440000")


class TestCreateTask:
    """Tests for POST /api/{user_id}/tasks"""

    def test_create_task_success(self, client, auth_headers):
        """Request with valid title creates task and returns 201."""
        response = client.post(
            f"/api/{TEST_USER_ID}/tasks",
            json={"title": "New Task", "description": "Task description"},
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Task"
        assert data["description"] == "Task description"
        assert data["completed"] is False
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_task_title_only(self, client, auth_headers):
        """Task can be created with title only."""
        response = client.post(
            f"/api/{TEST_USER_ID}/tasks",
            json={"title": "Title Only Task"},
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Title Only Task"
        assert data["description"] is None

    def test_create_task_missing_title(self, client, auth_headers):
        """Request without title returns 422."""
        response = client.post(
            f"/api/{TEST_USER_ID}/tasks",
            json={"description": "No title"},
            headers=auth_headers
        )

        assert response.status_code == 422

    def test_create_task_empty_title(self, client, auth_headers):
        """Request with empty title returns 422."""
        response = client.post(
            f"/api/{TEST_USER_ID}/tasks",
            json={"title": ""},
            headers=auth_headers
        )

        assert response.status_code == 422

    def test_create_task_whitespace_title(self, client, auth_headers):
        """Request with whitespace-only title returns 422."""
        response = client.post(
            f"/api/{TEST_USER_ID}/tasks",
            json={"title": "   "},
            headers=auth_headers
        )

        assert response.status_code == 422

    def test_create_task_title_max_length(self, client, auth_headers):
        """Title with 255 chars is accepted."""
        title = "x" * 255
        response = client.post(
            f"/api/{TEST_USER_ID}/tasks",
            json={"title": title},
            headers=auth_headers
        )

        assert response.status_code == 201
        assert response.json()["title"] == title

    def test_create_task_title_too_long(self, client, auth_headers):
        """Title with 256 chars returns 422."""
        title = "x" * 256
        response = client.post(
            f"/api/{TEST_USER_ID}/tasks",
            json={"title": title},
            headers=auth_headers
        )

        assert response.status_code == 422

    def test_create_task_no_auth(self, client_no_auth):
        """Request without JWT returns 401."""
        response = client_no_auth.post(
            f"/api/{TEST_USER_ID}/tasks",
            json={"title": "Test"}
        )

        assert response.status_code in [401, 403]

    def test_create_task_user_mismatch(self, client, auth_headers):
        """Request with mismatched user_id returns 403."""
        other_user_id = uuid4()
        response = client.post(
            f"/api/{other_user_id}/tasks",
            json={"title": "Test"},
            headers=auth_headers
        )

        assert response.status_code == 403


class TestListTasks:
    """Tests for GET /api/{user_id}/tasks"""

    def test_list_tasks_empty(self, client, auth_headers):
        """Returns empty array when user has no tasks."""
        response = client.get(
            f"/api/{TEST_USER_ID}/tasks",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["tasks"] == []
        assert data["count"] == 0

    def test_list_tasks_with_tasks(self, client, auth_headers, sample_task):
        """Returns array of tasks belonging to user."""
        response = client.get(
            f"/api/{TEST_USER_ID}/tasks",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["title"] == "Sample Task"

    def test_list_tasks_no_auth(self, client_no_auth):
        """Request without JWT returns 401."""
        response = client_no_auth.get(f"/api/{TEST_USER_ID}/tasks")

        assert response.status_code in [401, 403]


class TestGetTask:
    """Tests for GET /api/{user_id}/tasks/{task_id}"""

    def test_get_task_success(self, client, auth_headers, sample_task):
        """Returns task object for valid request."""
        response = client.get(
            f"/api/{TEST_USER_ID}/tasks/{sample_task.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_task.id)
        assert data["title"] == "Sample Task"
        assert "description" in data
        assert "completed" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_task_not_found(self, client, auth_headers):
        """Returns 404 when task_id does not exist."""
        fake_id = uuid4()
        response = client.get(
            f"/api/{TEST_USER_ID}/tasks/{fake_id}",
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_get_task_no_auth(self, client_no_auth, sample_task):
        """Request without JWT returns 401."""
        response = client_no_auth.get(
            f"/api/{TEST_USER_ID}/tasks/{sample_task.id}"
        )

        assert response.status_code in [401, 403]


class TestUpdateTask:
    """Tests for PUT /api/{user_id}/tasks/{task_id}"""

    def test_update_task_title(self, client, auth_headers, sample_task):
        """Allows updating title only."""
        response = client.put(
            f"/api/{TEST_USER_ID}/tasks/{sample_task.id}",
            json={"title": "Updated Title"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Sample description"

    def test_update_task_description(self, client, auth_headers, sample_task):
        """Allows updating description only."""
        response = client.put(
            f"/api/{TEST_USER_ID}/tasks/{sample_task.id}",
            json={"description": "Updated description"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Sample Task"
        assert data["description"] == "Updated description"

    def test_update_task_both(self, client, auth_headers, sample_task):
        """Allows updating both title and description."""
        response = client.put(
            f"/api/{TEST_USER_ID}/tasks/{sample_task.id}",
            json={"title": "New Title", "description": "New description"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title"
        assert data["description"] == "New description"

    def test_update_task_not_found(self, client, auth_headers):
        """Returns 404 when task_id does not exist."""
        fake_id = uuid4()
        response = client.put(
            f"/api/{TEST_USER_ID}/tasks/{fake_id}",
            json={"title": "Test"},
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_update_task_no_auth(self, client_no_auth, sample_task):
        """Request without JWT returns 401."""
        response = client_no_auth.put(
            f"/api/{TEST_USER_ID}/tasks/{sample_task.id}",
            json={"title": "Test"}
        )

        assert response.status_code in [401, 403]


class TestDeleteTask:
    """Tests for DELETE /api/{user_id}/tasks/{task_id}"""

    def test_delete_task_success(self, client, auth_headers, sample_task):
        """Returns 204 on successful deletion."""
        response = client.delete(
            f"/api/{TEST_USER_ID}/tasks/{sample_task.id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify task is deleted
        get_response = client.get(
            f"/api/{TEST_USER_ID}/tasks/{sample_task.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    def test_delete_task_not_found(self, client, auth_headers):
        """Returns 404 when task_id does not exist."""
        fake_id = uuid4()
        response = client.delete(
            f"/api/{TEST_USER_ID}/tasks/{fake_id}",
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_delete_task_no_auth(self, client_no_auth, sample_task):
        """Request without JWT returns 401."""
        response = client_no_auth.delete(
            f"/api/{TEST_USER_ID}/tasks/{sample_task.id}"
        )

        assert response.status_code in [401, 403]


class TestToggleCompletion:
    """Tests for PATCH /api/{user_id}/tasks/{task_id}/complete"""

    def test_toggle_incomplete_to_complete(self, client, auth_headers, sample_task):
        """Toggles completed from false to true."""
        assert sample_task.completed is False

        response = client.patch(
            f"/api/{TEST_USER_ID}/tasks/{sample_task.id}/complete",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is True

    def test_toggle_complete_to_incomplete(self, client, auth_headers, sample_task, session):
        """Toggles completed from true to false."""
        # Set task to completed
        sample_task.completed = True
        session.add(sample_task)
        session.commit()

        response = client.patch(
            f"/api/{TEST_USER_ID}/tasks/{sample_task.id}/complete",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is False

    def test_toggle_not_found(self, client, auth_headers):
        """Returns 404 when task_id does not exist."""
        fake_id = uuid4()
        response = client.patch(
            f"/api/{TEST_USER_ID}/tasks/{fake_id}/complete",
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_toggle_no_auth(self, client_no_auth, sample_task):
        """Request without JWT returns 401."""
        response = client_no_auth.patch(
            f"/api/{TEST_USER_ID}/tasks/{sample_task.id}/complete"
        )

        assert response.status_code in [401, 403]
