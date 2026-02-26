"""
챕터 01 - 첫 번째 Playwright 테스트

pytest-playwright 플러그인이 제공하는 `page` 픽스처를 통해
브라우저를 자동으로 관리합니다.

실행:
    pytest tests/01_basic/test_first_playwright.py -v
    pytest tests/01_basic/test_first_playwright.py -v --headed
"""
from playwright.sync_api import Page, expect


class TestFirstPlaywright:
    """Playwright 기초: 브라우저 자동화 첫 걸음."""

    def test_page_title(self, page: Page) -> None:
        """페이지 타이틀이 기대한 값인지 확인합니다."""
        page.goto("https://playwright.dev")

        # expect()는 단언(assertion) API
        # 타이틀에 "Playwright" 텍스트가 포함되어야 함
        expect(page).to_have_title("Fast and reliable end-to-end testing for modern web apps | Playwright")

    def test_page_url(self, page: Page) -> None:
        """페이지 이동 후 URL을 확인합니다."""
        page.goto("https://playwright.dev")

        # URL 검증
        expect(page).to_have_url("https://playwright.dev/")

    def test_navigate_to_docs(self, page: Page) -> None:
        """링크 클릭으로 페이지 이동을 확인합니다."""
        page.goto("https://playwright.dev")

        # "Docs" 링크 클릭
        page.get_by_role("link", name="Docs").click()

        # URL이 /docs 경로를 포함해야 함
        expect(page).to_have_url("https://playwright.dev/docs/intro")

    def test_browser_context_isolation(self, browser) -> None:
        """BrowserContext는 독립된 세션을 제공합니다 (쿠키 격리)."""
        # context 1: 독립 세션
        context1 = browser.new_context()
        page1 = context1.new_page()
        page1.goto("https://playwright.dev")

        # context 2: 또 다른 독립 세션 (쿠키가 공유되지 않음)
        context2 = browser.new_context()
        page2 = context2.new_page()
        page2.goto("https://playwright.dev")

        # 두 페이지 모두 정상적으로 로드됨
        expect(page1).to_have_url("https://playwright.dev/")
        expect(page2).to_have_url("https://playwright.dev/")

        context1.close()
        context2.close()

    def test_screenshot(self, page: Page, tmp_path) -> None:
        """스크린샷을 찍고 파일로 저장합니다."""
        page.goto("https://playwright.dev")

        screenshot_path = tmp_path / "playwright_home.png"
        page.screenshot(path=str(screenshot_path))

        # 파일이 생성됐는지 확인
        assert screenshot_path.exists()
        assert screenshot_path.stat().st_size > 0

    def test_viewport_size(self, page: Page) -> None:
        """뷰포트 크기를 변경하고 반응형 레이아웃을 테스트합니다."""
        # 모바일 사이즈로 설정
        page.set_viewport_size({"width": 375, "height": 812})
        page.goto("https://playwright.dev")

        # 페이지가 로드되었는지 확인
        expect(page).to_have_url("https://playwright.dev/")
