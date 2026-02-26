"""
챕터 03 - 사용자 액션

클릭, 입력, 키보드, 마우스 등 다양한 사용자 액션을 실습합니다.

실행:
    pytest tests/03_actions/ -v --headed
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def todo_page(page: Page) -> Page:
    """TodoMVC 앱으로 이동한 page."""
    page.goto("https://demo.playwright.dev/todomvc")
    return page


class TestNavigationActions:
    """페이지 이동 관련 액션."""

    def test_goto(self, page: Page) -> None:
        """URL로 직접 이동합니다."""
        page.goto("https://playwright.dev")
        expect(page).to_have_url("https://playwright.dev/")

    def test_goto_with_wait(self, page: Page) -> None:
        """페이지 이동 시 특정 이벤트를 기다립니다."""
        # networkidle: 네트워크 요청이 멈출 때까지 대기
        page.goto("https://playwright.dev", wait_until="networkidle")
        expect(page).to_have_url("https://playwright.dev/")

    def test_back_and_forward(self, page: Page) -> None:
        """브라우저 뒤로/앞으로 이동합니다."""
        page.goto("https://playwright.dev")
        page.goto("https://playwright.dev/docs/intro")

        # 뒤로
        page.go_back()
        expect(page).to_have_url("https://playwright.dev/")

        # 앞으로
        page.go_forward()
        expect(page).to_have_url("https://playwright.dev/docs/intro")

    def test_reload(self, page: Page) -> None:
        """페이지를 새로고침합니다."""
        page.goto("https://playwright.dev")
        page.reload()
        expect(page).to_have_url("https://playwright.dev/")


class TestClickActions:
    """클릭 관련 액션."""

    def test_simple_click(self, todo_page: Page) -> None:
        """일반 클릭."""
        todo_page.get_by_role("textbox", name="What needs to be done?").fill("Test task")
        todo_page.keyboard.press("Enter")

        # 체크박스 클릭 (완료 처리)
        todo_page.locator("ul.todo-list li").first.get_by_role("checkbox").click()

        # 완료된 항목 확인
        completed = todo_page.locator("li.completed")
        expect(completed).to_have_count(1)

    def test_click_with_options(self, page: Page) -> None:
        """클릭 옵션 활용."""
        page.goto("https://playwright.dev")

        # 더블 클릭
        # page.get_by_role("link", name="Docs").dblclick()

        # 우클릭
        # page.get_by_role("link", name="Docs").click(button="right")

        # 특정 위치 클릭 (요소 내 상대 좌표)
        # page.get_by_role("link", name="Docs").click(position={"x": 10, "y": 5})

        # Ctrl+클릭 (새 탭에서 열기)
        # page.get_by_role("link", name="Docs").click(modifiers=["Control"])

        # 현재는 단순히 페이지가 로드됐는지만 확인
        expect(page).to_have_url("https://playwright.dev/")

    def test_hover(self, page: Page) -> None:
        """요소에 마우스를 올립니다 (hover)."""
        page.goto("https://playwright.dev")
        page.get_by_role("link", name="Docs").hover()
        # hover 후 툴팁이나 드롭다운이 나타나는 경우 확인


class TestInputActions:
    """텍스트 입력 관련 액션."""

    def test_fill(self, todo_page: Page) -> None:
        """fill(): 입력값을 즉시 채웁니다 (기존 내용 교체)."""
        input_box = todo_page.get_by_role("textbox", name="What needs to be done?")

        input_box.fill("Buy groceries")
        input_box.fill("Buy vegetables")  # 기존 내용 교체됨

        # Enter로 추가
        todo_page.keyboard.press("Enter")

        expect(todo_page.locator("ul.todo-list li")).to_have_count(1)
        expect(todo_page.locator("ul.todo-list li").first).to_contain_text("Buy vegetables")

    def test_type(self, todo_page: Page) -> None:
        """type(): 실제 키보드 입력처럼 한 글자씩 입력합니다."""
        input_box = todo_page.get_by_role("textbox", name="What needs to be done?")

        # 실제 키 입력 시뮬레이션 (지연 효과 있음)
        input_box.press_sequentially("Buy milk", delay=50)
        todo_page.keyboard.press("Enter")

        expect(todo_page.locator("ul.todo-list li").first).to_contain_text("Buy milk")

    def test_clear(self, todo_page: Page) -> None:
        """입력 필드를 지웁니다."""
        input_box = todo_page.get_by_role("textbox", name="What needs to be done?")

        input_box.fill("잘못 입력한 내용")
        input_box.clear()

        expect(input_box).to_be_empty()


class TestKeyboardActions:
    """키보드 관련 액션."""

    def test_keyboard_press(self, todo_page: Page) -> None:
        """특정 키를 누릅니다."""
        input_box = todo_page.get_by_role("textbox", name="What needs to be done?")
        input_box.fill("Task 1")

        # Enter 키로 할 일 추가
        todo_page.keyboard.press("Enter")

        expect(todo_page.locator("ul.todo-list li")).to_have_count(1)

    def test_keyboard_shortcuts(self, todo_page: Page) -> None:
        """키보드 단축키를 입력합니다."""
        input_box = todo_page.get_by_role("textbox", name="What needs to be done?")
        input_box.fill("Some text here")

        # Ctrl+A (전체 선택)
        input_box.press("Control+a")

        # Ctrl+C, Ctrl+V (복사/붙여넣기)
        # input_box.press("Control+c")
        # input_box.press("Control+v")

        # 내용이 유지되는지 확인
        expect(input_box).not_to_be_empty()

    def test_tab_key(self, page: Page) -> None:
        """Tab 키로 포커스를 이동합니다."""
        page.goto("https://playwright.dev")

        # Tab 키 누르기
        page.keyboard.press("Tab")
        page.keyboard.press("Tab")
        # 포커스 이동 후 동작 확인 가능


class TestTodoWorkflow:
    """실제 사용 시나리오: TodoMVC 워크플로우."""

    def test_add_and_complete_todo(self, todo_page: Page) -> None:
        """할 일을 추가하고 완료 처리하는 전체 흐름."""
        input_box = todo_page.get_by_role("textbox", name="What needs to be done?")

        # 할 일 3개 추가
        for task in ["Buy milk", "Walk the dog", "Read a book"]:
            input_box.fill(task)
            todo_page.keyboard.press("Enter")

        # 전체 3개 확인
        expect(todo_page.locator("ul.todo-list li")).to_have_count(3)

        # 첫 번째 할 일 완료 처리
        todo_page.locator("ul.todo-list li").first.get_by_role("checkbox").click()

        # 'Active' 필터 클릭 → 2개만 보임
        todo_page.get_by_role("link", name="Active").click()
        expect(todo_page.locator("ul.todo-list li")).to_have_count(2)

        # 'Completed' 필터 클릭 → 1개만 보임
        todo_page.get_by_role("link", name="Completed").click()
        expect(todo_page.locator("ul.todo-list li")).to_have_count(1)
