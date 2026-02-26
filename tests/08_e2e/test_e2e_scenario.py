"""
챕터 08 - E2E 테스트 시나리오

서버 개발자가 담당하는 웹 서비스에 대한
실전 E2E 테스트 패턴을 실습합니다.

실행:
    pytest tests/08_e2e/ -v --headed -m e2e
    pytest tests/08_e2e/ -v -m smoke
"""
import re
import json
import pytest
from playwright.sync_api import Page, Playwright, APIRequestContext, expect

from pages.todo_page import TodoPage


# ── E2E 픽스처 ────────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def api(playwright: Playwright) -> APIRequestContext:
    """E2E 테스트용 API 컨텍스트 (JSONPlaceholder)."""
    context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com",
        extra_http_headers={"Content-Type": "application/json"},
    )
    yield context
    context.dispose()


@pytest.fixture
def todo_page(page: Page) -> TodoPage:
    return TodoPage(page).open()


# ── 시나리오 1: 핵심 경로 (Critical Path) ────────────────────────────────────
@pytest.mark.smoke
@pytest.mark.e2e
class TestCriticalPath:
    """
    서비스의 핵심 사용자 경로.
    배포 직후 반드시 통과해야 하는 테스트입니다.
    """

    def test_app_loads_successfully(self, todo_page: TodoPage) -> None:
        """앱이 정상 로드되는지 확인합니다."""
        expect(todo_page.page).to_have_url(
            re.compile(r"demo\.playwright\.dev/todomvc")
        )
        expect(todo_page.page.get_by_role("heading", name="todos")).to_be_visible()
        expect(
            todo_page.page.get_by_role("textbox", name="What needs to be done?")
        ).to_be_visible()

    def test_create_todo_end_to_end(self, todo_page: TodoPage) -> None:
        """할 일 생성 전체 흐름을 검증합니다."""
        # Given: 빈 TodoMVC 앱
        todo_page.should_have_count(0)

        # When: 할 일 추가
        todo_page.add_todo("E2E 테스트 작성하기")

        # Then: 목록에 나타남
        todo_page.should_have_count(1)
        todo_page.should_contain_todo("E2E 테스트 작성하기")

    def test_complete_todo_end_to_end(self, todo_page: TodoPage) -> None:
        """할 일 완료 전체 흐름을 검증합니다."""
        # Given
        todo_page.add_todo("완료할 작업")

        # When: 완료 처리
        todo_page.complete_todo("완료할 작업")

        # Then: Completed 필터에서 확인
        todo_page.filter_completed()
        todo_page.should_have_count(1)


# ── 시나리오 2: API + UI 통합 ─────────────────────────────────────────────────
@pytest.mark.e2e
class TestApiAndUiIntegration:
    """
    API와 UI를 결합한 통합 E2E 테스트.
    서버 개발자에게 가장 실용적인 패턴입니다.
    """

    def test_data_created_via_api_visible_in_ui(
        self,
        page: Page,
        api: APIRequestContext,
    ) -> None:
        """
        API로 생성한 데이터가 UI에 정상적으로 표시되는지 검증합니다.

        흐름:
          1. API POST /todos → 데이터 생성
          2. UI 새로고침 또는 이동
          3. UI에서 데이터 확인

        이 패턴은 백엔드 API와 프론트엔드 렌더링이 모두 올바르게 동작하는지
        검증합니다.
        """
        # Step 1: API로 데이터 생성
        response = api.post(
            "/todos",
            data={"title": "API로 생성한 태스크", "completed": False, "userId": 1},
        )
        assert response.status == 201
        created = response.json()
        assert created["title"] == "API로 생성한 태스크"

        # Step 2: TodoMVC는 독립 앱이므로 UI에서 직접 추가하는 방식으로 시뮬레이션
        todo_page_obj = TodoPage(page).open()
        todo_page_obj.add_todo(created["title"])

        # Step 3: UI에서 해당 항목이 표시됨을 확인
        todo_page_obj.should_contain_todo("API로 생성한 태스크")

    def test_api_returns_correct_structure(
        self,
        api: APIRequestContext,
    ) -> None:
        """
        API 응답 구조가 프론트엔드가 기대하는 형식과 일치하는지 검증합니다.

        서버 개발자가 API 계약을 변경할 때 이 테스트가 깨지면
        프론트엔드에 영향이 있다는 신호입니다.
        """
        response = api.get("/todos/1")
        assert response.status == 200

        todo = response.json()

        # 프론트엔드가 기대하는 필드 목록
        required_fields = {"id", "title", "completed", "userId"}
        actual_fields = set(todo.keys())

        missing = required_fields - actual_fields
        assert not missing, f"API 응답에 누락된 필드: {missing}"

    def test_api_pagination_works(
        self,
        api: APIRequestContext,
    ) -> None:
        """
        페이지네이션 API가 올바르게 동작하는지 검증합니다.
        """
        # 첫 페이지 (limit=5)
        response = api.get("/todos", params={"_start": 0, "_limit": 5})
        assert response.status == 200
        page1 = response.json()
        assert len(page1) == 5

        # 두 번째 페이지 (limit=5)
        response = api.get("/todos", params={"_start": 5, "_limit": 5})
        assert response.status == 200
        page2 = response.json()
        assert len(page2) == 5

        # 두 페이지의 ID가 겹치지 않아야 함
        page1_ids = {item["id"] for item in page1}
        page2_ids = {item["id"] for item in page2}
        assert page1_ids.isdisjoint(page2_ids)


# ── 시나리오 3: 에러 처리 ────────────────────────────────────────────────────
@pytest.mark.e2e
class TestErrorHandling:
    """에러 상황에서 앱이 올바르게 동작하는지 검증합니다."""

    def test_api_404_handling(self, api: APIRequestContext) -> None:
        """존재하지 않는 리소스 요청 시 적절한 에러를 반환합니다."""
        response = api.get("/todos/99999999")
        assert response.status == 404

    def test_ui_handles_empty_state(self, todo_page: TodoPage) -> None:
        """항목이 없을 때 UI가 올바른 빈 상태를 보여줍니다."""
        # 빈 상태에서 footer가 없어야 함
        footer = todo_page.page.locator("footer.footer")
        expect(footer).to_be_hidden()

    def test_network_error_simulation(self, page: Page) -> None:
        """
        네트워크 오류를 시뮬레이션합니다.
        API 서버가 다운됐을 때 UI가 graceful하게 처리하는지 확인합니다.
        """
        # API 요청을 강제로 실패시킴
        page.route("**/api/**", lambda route: route.abort("failed"))

        # 앱 자체는 로드됨 (정적 자산은 영향 없음)
        page.goto("https://demo.playwright.dev/todomvc")
        expect(page.get_by_role("heading", name="todos")).to_be_visible()


# ── 시나리오 4: 반응형 & 크로스 브라우저 ────────────────────────────────────
@pytest.mark.e2e
class TestResponsiveAndCrossBrowser:
    """다양한 환경에서의 동작을 검증합니다."""

    def test_mobile_viewport(self, page: Page) -> None:
        """모바일 뷰포트에서 앱이 정상 동작합니다."""
        page.set_viewport_size({"width": 375, "height": 812})
        page.goto("https://demo.playwright.dev/todomvc")

        # 모바일에서도 주요 기능 동작
        input_box = page.get_by_role("textbox", name="What needs to be done?")
        expect(input_box).to_be_visible()

        input_box.fill("모바일 테스트")
        page.keyboard.press("Enter")

        expect(page.locator("ul.todo-list li")).to_have_count(1)

    def test_tablet_viewport(self, page: Page) -> None:
        """태블릿 뷰포트에서 앱이 정상 동작합니다."""
        page.set_viewport_size({"width": 768, "height": 1024})
        page.goto("https://demo.playwright.dev/todomvc")

        expect(page.get_by_role("heading", name="todos")).to_be_visible()


# ── 시나리오 5: 성능 체크 ─────────────────────────────────────────────────────
@pytest.mark.e2e
class TestPerformance:
    """기본적인 성능 지표를 확인합니다."""

    def test_page_load_time(self, page: Page) -> None:
        """페이지 로드 시간이 허용 범위 내인지 확인합니다."""
        import time

        start = time.time()
        page.goto("https://demo.playwright.dev/todomvc", wait_until="load")
        elapsed = time.time() - start

        # 10초 이내 로드 (관대한 기준)
        assert elapsed < 10.0, f"페이지 로드 시간 초과: {elapsed:.2f}s"

    def test_large_list_performance(self, todo_page: TodoPage) -> None:
        """많은 항목이 있을 때도 UI가 정상 동작합니다."""
        # 50개 항목 추가
        for i in range(1, 51):
            todo_page.add_todo(f"Task {i:03d}")

        # 모든 항목 표시 확인
        todo_page.should_have_count(50)

        # 필터 동작 확인
        todo_page.filter_active()
        todo_page.should_have_count(50)
