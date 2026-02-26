"""
챕터 04 - 단언 (Assertions)

Playwright의 expect() API를 사용한 다양한 단언 방법을 실습합니다.
Auto-retrying assertion과 일반 assertion의 차이도 확인합니다.

실행:
    pytest tests/04_assertions/ -v --headed
"""
import re
import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def todo_page(page: Page) -> Page:
    page.goto("https://demo.playwright.dev/todomvc")
    return page


class TestPageAssertions:
    """Page 단위 단언."""

    def test_page_title(self, page: Page) -> None:
        """페이지 타이틀 확인."""
        page.goto("https://playwright.dev")
        expect(page).to_have_title("Fast and reliable end-to-end testing for modern web apps | Playwright")

    def test_page_title_regex(self, page: Page) -> None:
        """정규식으로 타이틀 확인."""
        page.goto("https://playwright.dev")
        expect(page).to_have_title(re.compile(r"Playwright"))

    def test_page_url(self, page: Page) -> None:
        """URL 정확히 일치 확인."""
        page.goto("https://playwright.dev")
        expect(page).to_have_url("https://playwright.dev/")

    def test_page_url_regex(self, page: Page) -> None:
        """URL 정규식 확인."""
        page.goto("https://playwright.dev/docs/intro")
        expect(page).to_have_url(re.compile(r"/docs/"))


class TestVisibilityAssertions:
    """가시성 관련 단언."""

    def test_to_be_visible(self, todo_page: Page) -> None:
        """요소가 보이는지 확인합니다."""
        input_box = todo_page.get_by_role("textbox", name="What needs to be done?")
        expect(input_box).to_be_visible()

    def test_to_be_hidden(self, todo_page: Page) -> None:
        """요소가 숨겨져 있는지 확인합니다."""
        # TodoMVC에서 할 일이 없으면 footer가 숨겨져 있음
        footer = todo_page.locator("footer.footer")
        expect(footer).to_be_hidden()

    def test_to_be_visible_after_action(self, todo_page: Page) -> None:
        """액션 이후 요소가 나타나는지 확인합니다."""
        # 할 일 추가 전에는 footer가 없음
        footer = todo_page.locator("footer.footer")
        expect(footer).to_be_hidden()

        # 할 일 추가
        todo_page.get_by_role("textbox", name="What needs to be done?").fill("Task")
        todo_page.keyboard.press("Enter")

        # 이제 footer가 보임
        expect(footer).to_be_visible()


class TestTextAssertions:
    """텍스트 관련 단언."""

    def test_to_have_text(self, todo_page: Page) -> None:
        """요소의 텍스트가 정확히 일치하는지 확인합니다."""
        todo_page.get_by_role("textbox", name="What needs to be done?").fill("Buy milk")
        todo_page.keyboard.press("Enter")

        # 정확한 텍스트
        expect(todo_page.locator("ul.todo-list li").first).to_have_text("Buy milk")

    def test_to_contain_text(self, todo_page: Page) -> None:
        """요소의 텍스트에 특정 문자열이 포함되어 있는지 확인합니다."""
        todo_page.get_by_role("textbox", name="What needs to be done?").fill("Buy groceries")
        todo_page.keyboard.press("Enter")

        # 부분 포함 확인
        expect(todo_page.locator("ul.todo-list li").first).to_contain_text("groceries")

    def test_to_have_text_regex(self, todo_page: Page) -> None:
        """정규식으로 텍스트를 확인합니다."""
        todo_page.get_by_role("textbox", name="What needs to be done?").fill("Buy milk 2개")
        todo_page.keyboard.press("Enter")

        expect(todo_page.locator("ul.todo-list li").first).to_have_text(re.compile(r"Buy .+"))

    def test_multiple_items_text(self, todo_page: Page) -> None:
        """여러 요소의 텍스트를 한 번에 확인합니다."""
        input_box = todo_page.get_by_role("textbox", name="What needs to be done?")
        for task in ["Task A", "Task B", "Task C"]:
            input_box.fill(task)
            todo_page.keyboard.press("Enter")

        # 모든 항목의 텍스트 목록 확인
        expect(todo_page.locator("ul.todo-list li")).to_have_text(["Task A", "Task B", "Task C"])


class TestCountAssertions:
    """카운트 관련 단언."""

    def test_to_have_count(self, todo_page: Page) -> None:
        """요소 개수를 확인합니다."""
        input_box = todo_page.get_by_role("textbox", name="What needs to be done?")

        input_box.fill("Task 1")
        todo_page.keyboard.press("Enter")
        expect(todo_page.locator("ul.todo-list li")).to_have_count(1)

        input_box.fill("Task 2")
        todo_page.keyboard.press("Enter")
        expect(todo_page.locator("ul.todo-list li")).to_have_count(2)

    def test_count_after_delete(self, todo_page: Page) -> None:
        """삭제 후 개수가 줄어드는지 확인합니다."""
        input_box = todo_page.get_by_role("textbox", name="What needs to be done?")
        input_box.fill("Task to delete")
        todo_page.keyboard.press("Enter")
        expect(todo_page.locator("ul.todo-list li")).to_have_count(1)

        # 항목에 호버 → 삭제 버튼 표시 → 클릭
        item = todo_page.locator("ul.todo-list li").first
        item.hover()
        item.get_by_role("button", name="Delete").click()

        expect(todo_page.locator("ul.todo-list li")).to_have_count(0)


class TestStateAssertions:
    """요소 상태 관련 단언."""

    def test_to_be_enabled_disabled(self, page: Page) -> None:
        """버튼이 활성화/비활성화 상태인지 확인합니다."""
        page.goto("https://playwright.dev")

        link = page.get_by_role("link", name="Docs")
        expect(link).to_be_enabled()

    def test_to_be_checked(self, todo_page: Page) -> None:
        """체크박스 상태를 확인합니다."""
        todo_page.get_by_role("textbox", name="What needs to be done?").fill("Task")
        todo_page.keyboard.press("Enter")

        checkbox = todo_page.locator("ul.todo-list li").first.get_by_role("checkbox")

        # 처음에는 체크 안 됨
        expect(checkbox).not_to_be_checked()

        # 클릭 후 체크됨
        checkbox.click()
        expect(checkbox).to_be_checked()

    def test_to_be_empty(self, todo_page: Page) -> None:
        """입력 필드가 비어있는지 확인합니다."""
        input_box = todo_page.get_by_role("textbox", name="What needs to be done?")
        expect(input_box).to_be_empty()


class TestAttributeAssertions:
    """속성 관련 단언."""

    def test_to_have_attribute(self, page: Page) -> None:
        """요소의 HTML 속성을 확인합니다."""
        page.goto("https://playwright.dev")

        # href 속성 확인
        link = page.get_by_role("link", name="Docs")
        expect(link).to_have_attribute("href", "/docs/intro")

    def test_to_have_class(self, todo_page: Page) -> None:
        """요소의 CSS 클래스를 확인합니다."""
        todo_page.get_by_role("textbox", name="What needs to be done?").fill("Task")
        todo_page.keyboard.press("Enter")

        # 완료 처리
        todo_page.locator("ul.todo-list li").first.get_by_role("checkbox").click()

        # 완료된 항목은 'completed' 클래스를 가짐
        expect(todo_page.locator("ul.todo-list li").first).to_have_class(re.compile("completed"))

    def test_to_have_value(self, todo_page: Page) -> None:
        """입력 필드의 현재 값을 확인합니다."""
        input_box = todo_page.get_by_role("textbox", name="What needs to be done?")
        input_box.fill("My task")

        expect(input_box).to_have_value("My task")
