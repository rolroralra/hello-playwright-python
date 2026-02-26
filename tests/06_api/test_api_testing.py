"""
챕터 06 - API 테스팅

Playwright의 APIRequestContext를 사용해 HTTP 요청을 직접 테스트합니다.
UI 테스트와 API 테스트를 함께 활용하는 방법도 실습합니다.

실행:
    pytest tests/06_api/ -v
"""
import pytest
from playwright.sync_api import APIRequestContext, Page, Playwright, expect


# ── APIRequestContext 픽스처 ────────────────────────────────────────────────
@pytest.fixture(scope="session")
def api_request_context(playwright: Playwright) -> APIRequestContext:
    """세션 전체에서 재사용하는 API 요청 컨텍스트."""
    context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com",
        extra_http_headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    yield context
    context.dispose()


class TestGetRequest:
    """HTTP GET 요청 테스트."""

    def test_get_todos(self, api_request_context: APIRequestContext) -> None:
        """전체 TODO 목록을 조회합니다."""
        response = api_request_context.get("/todos")

        assert response.status == 200
        todos = response.json()
        assert isinstance(todos, list)
        assert len(todos) > 0  # JSONPlaceholder는 여러 TODO를 반환

    def test_get_single_todo(self, api_request_context: APIRequestContext) -> None:
        """단건 TODO를 조회합니다."""
        response = api_request_context.get("/todos/1")

        assert response.status == 200
        todo = response.json()
        assert todo["id"] == 1
        assert "title" in todo
        assert "completed" in todo
        assert "userId" in todo

    def test_get_user(self, api_request_context: APIRequestContext) -> None:
        """사용자 정보를 조회합니다."""
        response = api_request_context.get("/users/1")

        assert response.status == 200
        user = response.json()
        assert user["id"] == 1
        assert "name" in user
        assert "email" in user

    def test_get_with_query_params(self, api_request_context: APIRequestContext) -> None:
        """쿼리 파라미터로 필터링합니다."""
        response = api_request_context.get(
            "/todos",
            params={"userId": 1, "completed": "true"},
        )

        assert response.status == 200
        todos = response.json()
        # userId=1의 completed todos만 반환
        for todo in todos:
            assert todo["userId"] == 1
            assert todo["completed"] is True

    def test_not_found(self, api_request_context: APIRequestContext) -> None:
        """존재하지 않는 리소스 요청 시 404 응답 확인."""
        response = api_request_context.get("/todos/99999")
        assert response.status == 404


class TestPostRequest:
    """HTTP POST 요청 테스트."""

    def test_create_todo(self, api_request_context: APIRequestContext) -> None:
        """새 TODO를 생성합니다."""
        new_todo = {
            "title": "Playwright E2E 테스트 작성",
            "completed": False,
            "userId": 1,
        }

        response = api_request_context.post("/todos", data=new_todo)

        assert response.status == 201  # Created
        created = response.json()
        assert created["title"] == new_todo["title"]
        assert created["completed"] == new_todo["completed"]
        assert "id" in created  # 서버가 ID를 부여

    def test_create_post(self, api_request_context: APIRequestContext) -> None:
        """새 포스트를 생성합니다."""
        new_post = {
            "title": "테스트 포스트",
            "body": "Playwright로 API 테스트를 작성합니다.",
            "userId": 1,
        }

        response = api_request_context.post("/posts", data=new_post)

        assert response.status == 201
        post = response.json()
        assert post["title"] == new_post["title"]


class TestPutRequest:
    """HTTP PUT 요청 테스트."""

    def test_update_todo(self, api_request_context: APIRequestContext) -> None:
        """TODO를 전체 업데이트합니다."""
        updated_todo = {
            "id": 1,
            "title": "업데이트된 TODO",
            "completed": True,
            "userId": 1,
        }

        response = api_request_context.put("/todos/1", data=updated_todo)

        assert response.status == 200
        todo = response.json()
        assert todo["title"] == updated_todo["title"]
        assert todo["completed"] is True


class TestPatchRequest:
    """HTTP PATCH 요청 테스트."""

    def test_patch_todo(self, api_request_context: APIRequestContext) -> None:
        """TODO를 부분 업데이트합니다."""
        response = api_request_context.patch(
            "/todos/1",
            data={"completed": True},
        )

        assert response.status == 200
        todo = response.json()
        assert todo["completed"] is True


class TestDeleteRequest:
    """HTTP DELETE 요청 테스트."""

    def test_delete_todo(self, api_request_context: APIRequestContext) -> None:
        """TODO를 삭제합니다."""
        response = api_request_context.delete("/todos/1")
        assert response.status == 200


class TestResponseHeaders:
    """응답 헤더 테스트."""

    def test_content_type_header(self, api_request_context: APIRequestContext) -> None:
        """응답 Content-Type 헤더를 확인합니다."""
        response = api_request_context.get("/todos/1")

        content_type = response.headers.get("content-type", "")
        assert "application/json" in content_type

    def test_all_headers(self, api_request_context: APIRequestContext) -> None:
        """모든 응답 헤더를 출력합니다."""
        response = api_request_context.get("/todos/1")

        headers = response.headers
        assert headers is not None
        # 최소한 헤더가 존재해야 함
        assert len(headers) > 0


class TestApiAndUiCombined:
    """API와 UI를 결합한 테스트 — 서버 개발자에게 중요한 패턴."""

    def test_api_setup_then_verify_ui(self, page: Page, playwright: Playwright) -> None:
        """
        API로 데이터를 준비하고, UI에서 결과를 확인합니다.

        패턴:
        1. API로 테스트 데이터 생성 (빠름)
        2. UI에서 해당 데이터가 표시되는지 확인 (실제 사용자 경험 검증)
        """
        # Step 1: API로 TODO 생성
        api_context = playwright.request.new_context(
            base_url="https://jsonplaceholder.typicode.com"
        )
        response = api_context.post(
            "/todos",
            data={"title": "API로 생성한 할 일", "completed": False, "userId": 1},
        )
        assert response.status == 201
        created_todo = response.json()
        api_context.dispose()

        # Step 2: TodoMVC UI에서 직접 할 일 추가 (이 예시에서는 UI로 시뮬레이션)
        page.goto("https://demo.playwright.dev/todomvc")
        page.get_by_role("textbox", name="What needs to be done?").fill(
            created_todo["title"]
        )
        page.keyboard.press("Enter")

        # Step 3: UI에서 항목이 보이는지 확인
        expect(page.get_by_role("listitem").first).to_contain_text(
            created_todo["title"]
        )

    def test_ui_action_then_verify_api(self, page: Page, playwright: Playwright) -> None:
        """
        UI에서 액션을 수행하고, API로 결과를 검증합니다.

        패턴:
        1. UI에서 사용자 행동 시뮬레이션
        2. API 응답으로 백엔드 상태 검증
        """
        # Step 1: API로 현재 상태 확인
        api_context = playwright.request.new_context(
            base_url="https://jsonplaceholder.typicode.com"
        )
        get_response = api_context.get("/todos/1")
        assert get_response.status == 200
        original_todo = get_response.json()

        # Step 2: API로 상태 변경 (UI 행동 대신)
        update_response = api_context.patch(
            f"/todos/{original_todo['id']}",
            data={"completed": not original_todo["completed"]},
        )
        assert update_response.status == 200
        updated = update_response.json()
        assert updated["completed"] != original_todo["completed"]

        api_context.dispose()
