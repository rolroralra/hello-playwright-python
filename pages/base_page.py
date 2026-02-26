"""
Base Page - 모든 Page Object의 부모 클래스.

공통 기능(네비게이션, 스크린샷, URL 확인 등)을 제공합니다.
"""
from playwright.sync_api import Page, expect


class BasePage:
    """모든 Page Object가 상속하는 기반 클래스."""

    def __init__(self, page: Page) -> None:
        self.page = page

    # ── 네비게이션 ────────────────────────────────────────────────────────────
    def navigate(self, url: str) -> None:
        """URL로 이동합니다."""
        self.page.goto(url)

    def reload(self) -> None:
        """페이지를 새로고침합니다."""
        self.page.reload()

    # ── URL / 타이틀 ─────────────────────────────────────────────────────────
    @property
    def current_url(self) -> str:
        return self.page.url

    @property
    def title(self) -> str:
        return self.page.title()

    def wait_for_url(self, url: str, timeout: int = 5_000) -> None:
        self.page.wait_for_url(url, timeout=timeout)

    # ── 스크린샷 ─────────────────────────────────────────────────────────────
    def take_screenshot(self, path: str) -> None:
        """스크린샷을 찍어 저장합니다."""
        self.page.screenshot(path=path)
