"""
Todo Page - TodoMVC 앱의 Page Object.

UI 구현 세부사항(셀렉터 등)을 캡슐화하고,
테스트 코드에서는 비즈니스 언어로 상호작용합니다.
"""
import re as re_module
from playwright.sync_api import Page, Locator, expect

from pages.base_page import BasePage


class TodoPage(BasePage):
    """https://demo.playwright.dev/todomvc 페이지."""

    URL = "https://demo.playwright.dev/todomvc"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # 로케이터 정의 — 셀렉터를 한 곳에서 관리
        self._input = page.get_by_role("textbox", name="What needs to be done?")
        # ul.todo-list 안의 li만 타겟팅 (필터 링크의 li와 구분)
        self._todo_items = page.locator("ul.todo-list li")
        self._footer = page.locator("footer.footer")
        self._items_left = page.locator("span.todo-count")

    # ── 진입점 ────────────────────────────────────────────────────────────────
    def open(self) -> "TodoPage":
        """TodoMVC 앱을 엽니다."""
        self.navigate(self.URL)
        return self

    # ── 액션 ─────────────────────────────────────────────────────────────────
    def add_todo(self, text: str) -> "TodoPage":
        """할 일을 추가합니다."""
        self._input.fill(text)
        self.page.keyboard.press("Enter")
        return self

    def add_todos(self, *texts: str) -> "TodoPage":
        """여러 할 일을 한 번에 추가합니다."""
        for text in texts:
            self.add_todo(text)
        return self

    def complete_todo(self, text: str) -> "TodoPage":
        """특정 텍스트의 할 일을 완료 처리합니다."""
        item = self._todo_items.filter(has_text=text)
        item.get_by_role("checkbox").click()
        return self

    def delete_todo(self, text: str) -> "TodoPage":
        """특정 텍스트의 할 일을 삭제합니다."""
        item = self._todo_items.filter(has_text=text)
        item.hover()
        item.get_by_role("button", name="Delete").click()
        return self

    def clear_completed(self) -> "TodoPage":
        """완료된 항목을 모두 삭제합니다."""
        self.page.get_by_role("button", name="Clear completed").click()
        return self

    # ── 필터 ─────────────────────────────────────────────────────────────────
    def filter_all(self) -> "TodoPage":
        self.page.get_by_role("link", name="All").click()
        return self

    def filter_active(self) -> "TodoPage":
        self.page.get_by_role("link", name="Active").click()
        return self

    def filter_completed(self) -> "TodoPage":
        self.page.get_by_role("link", name="Completed").click()
        return self

    # ── 조회 ─────────────────────────────────────────────────────────────────
    def get_todo_count(self) -> int:
        """현재 표시된 할 일 개수를 반환합니다."""
        return self._todo_items.count()

    def get_items_left_text(self) -> str:
        """'n items left' 텍스트를 반환합니다."""
        return self._items_left.inner_text()

    # ── 단언 (Assertion Helpers) ─────────────────────────────────────────────
    def should_have_count(self, count: int) -> "TodoPage":
        expect(self._todo_items).to_have_count(count)
        return self

    def should_contain_todo(self, text: str) -> "TodoPage":
        expect(self._todo_items.filter(has_text=text)).to_have_count(1)
        return self

    def should_not_contain_todo(self, text: str) -> "TodoPage":
        expect(self._todo_items.filter(has_text=text)).to_have_count(0)
        return self

    def should_be_completed(self, text: str) -> "TodoPage":
        item = self._todo_items.filter(has_text=text)
        expect(item).to_have_class(re_module.compile(r"completed"))
        return self
