"""
챕터 05 - 대기 전략 & 네트워크 인터셉트

Auto-waiting, 명시적 대기, 네트워크 요청 인터셉트를 실습합니다.

실행:
    pytest tests/05_waiting/ -v --headed
"""
import re
import json
import pytest
from playwright.sync_api import Page, Route, Request, Response, expect


@pytest.fixture
def todo_page(page: Page) -> Page:
    page.goto("https://demo.playwright.dev/todomvc")
    return page


class TestAutoWaiting:
    """Playwright의 Auto-waiting 동작 확인."""

    def test_auto_wait_for_visible(self, todo_page: Page) -> None:
        """요소가 보일 때까지 자동으로 기다립니다."""
        # Playwright는 click() 전에 요소가 visible, stable, enabled 상태인지 자동 검사
        input_box = todo_page.get_by_role("textbox", name="What needs to be done?")

        # auto-waiting이 내부적으로 동작
        input_box.fill("Auto-wait task")
        todo_page.keyboard.press("Enter")

        expect(todo_page.locator("ul.todo-list li")).to_have_count(1)

    def test_wait_for_load_state(self, page: Page) -> None:
        """페이지 로드 완료를 기다립니다."""
        page.goto("https://playwright.dev")

        # load: 모든 리소스 로드 완료
        page.wait_for_load_state("load")

        # domcontentloaded: DOM만 파싱 완료
        # page.wait_for_load_state("domcontentloaded")

        # networkidle: 네트워크 요청이 500ms 이상 없을 때
        # page.wait_for_load_state("networkidle")

        expect(page).to_have_url("https://playwright.dev/")

    def test_wait_for_url(self, page: Page) -> None:
        """특정 URL로 이동될 때까지 기다립니다."""
        page.goto("https://playwright.dev")
        page.get_by_role("link", name="Docs").click()

        # URL이 변경될 때까지 대기
        page.wait_for_url("https://playwright.dev/docs/intro")
        expect(page).to_have_url("https://playwright.dev/docs/intro")


class TestExplicitWaiting:
    """명시적 대기 전략."""

    def test_wait_for_selector(self, todo_page: Page) -> None:
        """특정 셀렉터가 나타날 때까지 기다립니다."""
        input_box = todo_page.get_by_role("textbox", name="What needs to be done?")
        input_box.fill("Task")
        todo_page.keyboard.press("Enter")

        # todo-list가 나타날 때까지 대기
        todo_page.wait_for_selector("ul.todo-list li")

        expect(todo_page.locator("ul.todo-list li")).to_have_count(1)

    def test_wait_for_function(self, page: Page) -> None:
        """JavaScript 함수가 true를 반환할 때까지 기다립니다."""
        page.goto("https://playwright.dev")

        # 페이지가 완전히 로드될 때까지 (document.readyState가 'complete'일 때)
        page.wait_for_function("document.readyState === 'complete'")

        expect(page).to_have_url("https://playwright.dev/")

    def test_wait_for_timeout(self, page: Page) -> None:
        """명시적으로 특정 시간만큼 기다립니다.

        주의: 가능하면 사용하지 말고, 다른 대기 전략을 우선 시도하세요.
        flaky test의 원인이 됩니다.
        """
        page.goto("https://playwright.dev")

        # 500ms 대기 (나쁜 예시 — 꼭 필요한 경우에만)
        page.wait_for_timeout(500)

        expect(page).to_have_url("https://playwright.dev/")


class TestNetworkIntercept:
    """네트워크 요청 인터셉트."""

    def test_route_abort(self, page: Page) -> None:
        """특정 요청을 차단합니다 (광고, 분석 등 불필요한 요청 제거)."""
        # 이미지 요청 차단 (테스트 속도 향상)
        page.route("**/*.png", lambda route: route.abort())
        page.route("**/*.jpg", lambda route: route.abort())

        page.goto("https://playwright.dev")

        # 페이지는 정상 로드됨
        expect(page).to_have_url("https://playwright.dev/")

    def test_route_mock_response(self, page: Page) -> None:
        """API 응답을 가짜 데이터로 교체합니다."""
        # JSONPlaceholder의 /todos/1 응답 모킹
        mock_data = {"id": 1, "title": "Mock Todo Item", "completed": False}

        page.route(
            "https://jsonplaceholder.typicode.com/todos/1",
            lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(mock_data),
            ),
        )

        # API 요청 후 JavaScript로 결과 확인
        response = page.evaluate("""
            async () => {
                const res = await fetch('https://jsonplaceholder.typicode.com/todos/1');
                return res.json();
            }
        """)

        assert response["title"] == "Mock Todo Item"

    def test_route_modify_response(self, page: Page) -> None:
        """기존 API 응답을 가로채서 수정합니다."""
        def handle_route(route: Route) -> None:
            # 원래 요청을 실행
            response = route.fetch()
            # 응답 데이터 파싱
            data = response.json()
            # 데이터 수정
            data["title"] = "[수정됨] " + data.get("title", "")
            # 수정된 응답 반환
            route.fulfill(
                response=response,
                json=data,
            )

        page.route("https://jsonplaceholder.typicode.com/todos/1", handle_route)

        response = page.evaluate("""
            async () => {
                const res = await fetch('https://jsonplaceholder.typicode.com/todos/1');
                return res.json();
            }
        """)

        assert response["title"].startswith("[수정됨]")


class TestRequestCapture:
    """네트워크 요청/응답 캡처."""

    def test_capture_request(self, page: Page) -> None:
        """페이지 로드 시 발생하는 요청을 캡처합니다."""
        requests: list[Request] = []

        page.on("request", lambda req: requests.append(req))

        page.goto("https://playwright.dev")

        # 최소 1개 이상의 요청이 발생했어야 함
        assert len(requests) > 0

        # 첫 번째 요청은 메인 HTML 요청
        assert requests[0].url == "https://playwright.dev/"

    def test_wait_for_response(self, page: Page) -> None:
        """특정 API 응답을 기다립니다."""
        page.goto("https://playwright.dev")

        # 특정 URL 패턴의 응답을 기다림
        with page.expect_response("https://playwright.dev/") as response_info:
            page.reload()

        response = response_info.value
        assert response.status == 200

    def test_wait_for_request(self, page: Page) -> None:
        """특정 요청이 발생할 때까지 기다립니다."""
        page.goto("https://playwright.dev")

        # glob 패턴으로 URL 매칭, 캐시 우회를 위해 reload 사용
        with page.expect_request(re.compile(r"playwright\.dev")) as request_info:
            page.reload()

        request = request_info.value
        assert "playwright.dev" in request.url
