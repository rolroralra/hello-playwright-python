"""
챕터 07 - Page Object Model (POM)

셀렉터와 액션을 Page 클래스에 캡슐화해서 유지보수성을 높입니다.
테스트 코드는 비즈니스 언어로 작성됩니다.

실행:
    pytest tests/07_pom/ -v --headed
"""
import pytest
from playwright.sync_api import Page

from pages.todo_page import TodoPage


@pytest.fixture
def todo_page(page: Page) -> TodoPage:
    """열린 TodoPage 픽스처."""
    return TodoPage(page).open()


class TestTodoPageWithPom:
    """POM을 사용한 TodoMVC 테스트."""

    def test_add_single_todo(self, todo_page: TodoPage) -> None:
        """할 일 하나를 추가합니다."""
        todo_page.add_todo("Buy milk")
        todo_page.should_have_count(1)
        todo_page.should_contain_todo("Buy milk")

    def test_add_multiple_todos(self, todo_page: TodoPage) -> None:
        """여러 할 일을 추가합니다."""
        todo_page.add_todos("Task 1", "Task 2", "Task 3")
        todo_page.should_have_count(3)

    def test_complete_todo(self, todo_page: TodoPage) -> None:
        """할 일을 완료 처리합니다."""
        todo_page.add_todo("Buy eggs")
        todo_page.complete_todo("Buy eggs")
        todo_page.should_be_completed("Buy eggs")

    def test_delete_todo(self, todo_page: TodoPage) -> None:
        """할 일을 삭제합니다."""
        todo_page.add_todos("Keep this", "Delete this")
        todo_page.delete_todo("Delete this")

        todo_page.should_have_count(1)
        todo_page.should_contain_todo("Keep this")
        todo_page.should_not_contain_todo("Delete this")

    def test_filter_active_todos(self, todo_page: TodoPage) -> None:
        """Active 필터로 미완료 항목만 표시합니다."""
        todo_page.add_todos("Active task", "Done task")
        todo_page.complete_todo("Done task")

        todo_page.filter_active()
        todo_page.should_have_count(1)
        todo_page.should_contain_todo("Active task")

    def test_filter_completed_todos(self, todo_page: TodoPage) -> None:
        """Completed 필터로 완료 항목만 표시합니다."""
        todo_page.add_todos("Active task", "Done task")
        todo_page.complete_todo("Done task")

        todo_page.filter_completed()
        todo_page.should_have_count(1)
        todo_page.should_contain_todo("Done task")

    def test_method_chaining(self, todo_page: TodoPage) -> None:
        """메서드 체이닝으로 읽기 좋은 테스트 작성."""
        (
            todo_page
            .add_todos("Task A", "Task B", "Task C")
            .complete_todo("Task B")
            .filter_active()
            .should_have_count(2)
        )


class TestComplexScenario:
    """복잡한 시나리오 — POM 덕분에 가독성 유지."""

    def test_todo_workflow(self, todo_page: TodoPage) -> None:
        """
        시나리오: 하루의 할 일 관리 워크플로우

        1. 할 일 목록 생성
        2. 일부 완료 처리
        3. 미완료 항목만 필터
        4. 완료 항목 정리
        5. 최종 상태 확인
        """
        # 할 일 추가
        todo_page.add_todos(
            "아침 운동",
            "코드 리뷰",
            "점심 식사",
            "E2E 테스트 작성",
            "퇴근",
        )
        todo_page.should_have_count(5)

        # 일부 완료
        todo_page.complete_todo("아침 운동")
        todo_page.complete_todo("코드 리뷰")
        todo_page.complete_todo("점심 식사")

        # Active 필터 → 2개 남음
        todo_page.filter_active()
        todo_page.should_have_count(2)

        # Completed 필터 → 3개
        todo_page.filter_completed()
        todo_page.should_have_count(3)

        # 완료된 항목 삭제
        todo_page.clear_completed()

        # All 필터 → 2개만 남음
        todo_page.filter_all()
        todo_page.should_have_count(2)
        todo_page.should_contain_todo("E2E 테스트 작성")
        todo_page.should_contain_todo("퇴근")
