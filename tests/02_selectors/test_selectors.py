"""
챕터 02 - Playwright 셀렉터

요소를 찾는 다양한 방법을 실습합니다.
권장 우선순위: role > text > testid > css > xpath

실행:
    pytest tests/02_selectors/ -v --headed
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def todo_page(page: Page) -> Page:
    """TodoMVC 앱으로 이동한 page."""
    page.goto("https://demo.playwright.dev/todomvc")
    return page


class TestRoleSelector:
    """Role 셀렉터 - 접근성 기반, 가장 권장되는 방식."""

    def test_get_by_role_textbox(self, todo_page: Page) -> None:
        """role=textbox로 입력 필드를 찾습니다."""
        input_box = todo_page.get_by_role("textbox", name="What needs to be done?")

        # 요소가 보이는지 확인
        expect(input_box).to_be_visible()

    def test_get_by_role_button(self, page: Page) -> None:
        """role=button으로 버튼을 찾습니다."""
        page.goto("https://playwright.dev")

        # 'Get started' 버튼/링크 찾기
        get_started = page.get_by_role("link", name="Get started")
        expect(get_started).to_be_visible()

    def test_get_by_role_heading(self, todo_page: Page) -> None:
        """role=heading으로 제목 요소를 찾습니다."""
        heading = todo_page.get_by_role("heading", name="todos")
        expect(heading).to_be_visible()

    def test_get_by_role_listitem(self, todo_page: Page) -> None:
        """할 일을 추가하고 listitem으로 확인합니다."""
        # 할 일 추가
        todo_page.get_by_role("textbox", name="What needs to be done?").fill("Buy milk")
        todo_page.keyboard.press("Enter")

        # todo-list 내 listitem으로 확인 (필터 링크의 li와 구분하기 위해 범위 지정)
        items = todo_page.locator("ul.todo-list").get_by_role("listitem")
        expect(items).to_have_count(1)


class TestTextSelector:
    """Text 셀렉터 - 텍스트 내용으로 요소 탐색."""

    def test_get_by_text(self, page: Page) -> None:
        """텍스트 내용으로 요소를 찾습니다."""
        page.goto("https://playwright.dev")

        # 정확히 일치하는 텍스트
        element = page.get_by_text("Playwright enables reliable web automation")
        expect(element).to_be_visible()

    def test_get_by_text_partial(self, page: Page) -> None:
        """부분 텍스트로 요소를 찾습니다."""
        page.goto("https://playwright.dev")

        # exact=False 옵션 (기본값)으로 부분 일치
        elements = page.get_by_text("Docs", exact=True)
        expect(elements.first).to_be_visible()

    def test_get_by_label(self, page: Page) -> None:
        """label 텍스트로 입력 필드를 찾습니다."""
        # label과 연결된 input 찾기
        page.goto("https://demo.playwright.dev/todomvc")

        # placeholder 텍스트로 찾기 (label 대용)
        input_field = page.get_by_placeholder("What needs to be done?")
        expect(input_field).to_be_visible()


class TestLocatorChaining:
    """로케이터 체이닝 - 범위를 좁혀서 정확하게 찾기."""

    def test_filter_by_text(self, todo_page: Page) -> None:
        """여러 항목 중 특정 텍스트가 있는 것만 필터링합니다."""
        # 할 일 두 개 추가
        input_box = todo_page.get_by_role("textbox", name="What needs to be done?")
        input_box.fill("Buy milk")
        todo_page.keyboard.press("Enter")
        input_box.fill("Buy eggs")
        todo_page.keyboard.press("Enter")

        # 'Buy milk' 텍스트가 있는 listitem만 찾기
        milk_item = todo_page.get_by_role("listitem").filter(has_text="Buy milk")
        expect(milk_item).to_have_count(1)

    def test_nth_element(self, todo_page: Page) -> None:
        """n번째 요소를 선택합니다."""
        input_box = todo_page.get_by_role("textbox", name="What needs to be done?")
        input_box.fill("Task 1")
        todo_page.keyboard.press("Enter")
        input_box.fill("Task 2")
        todo_page.keyboard.press("Enter")
        input_box.fill("Task 3")
        todo_page.keyboard.press("Enter")

        # todo-list 내 항목만 선택 (필터 링크 제외)
        items = todo_page.locator("ul.todo-list li")

        # 첫 번째 항목
        expect(items.first).to_contain_text("Task 1")

        # 마지막 항목
        expect(items.last).to_contain_text("Task 3")

        # n번째 항목 (0-indexed)
        expect(items.nth(1)).to_contain_text("Task 2")


class TestCssAndXpathSelector:
    """CSS / XPath 셀렉터 - 레거시 코드나 복잡한 구조에서 사용."""

    def test_css_selector(self, todo_page: Page) -> None:
        """CSS 셀렉터로 요소를 찾습니다."""
        # CSS 선택자 (가능하면 role 셀렉터를 권장)
        input_field = todo_page.locator(".new-todo")
        expect(input_field).to_be_visible()

    def test_css_class_selector(self, todo_page: Page) -> None:
        """CSS 클래스로 요소 목록을 찾습니다."""
        # 할 일 추가
        input_box = todo_page.get_by_placeholder("What needs to be done?")
        input_box.fill("Test item")
        todo_page.keyboard.press("Enter")

        todo_items = todo_page.locator("ul.todo-list li")
        expect(todo_items).to_have_count(1)

    def test_xpath_selector(self, todo_page: Page) -> None:
        """XPath로 요소를 찾습니다 (마지막 수단으로만 사용)."""
        heading = todo_page.locator("//h1[text()='todos']")
        expect(heading).to_be_visible()
