# 09. Page Object Model (POM)

## POM이란?

Page Object Model은 UI 테스트의 유지보수성을 높이는 디자인 패턴입니다.

### 핵심 원칙

```
테스트 코드 ─────────────────────────────────────────────
  "로그인 버튼을 클릭한다"
           │
           ▼
Page Object ─────────────────────────────────────────────
  "로그인 버튼을 클릭하는 방법(셀렉터, 액션)을 캡슐화"
           │
           ▼
브라우저 ─────────────────────────────────────────────────
  실제 DOM 조작
```

### POM 없이 vs POM 있이

**POM 없이 (나쁜 예)**
```python
def test_login():
    page.locator("input#email").fill("user@example.com")
    page.locator("input#password").fill("pass")
    page.locator("button.btn-submit").click()
    # 버튼 CSS가 바뀌면 모든 테스트를 수정해야 함
```

**POM 있이 (좋은 예)**
```python
def test_login(login_page: LoginPage):
    login_page.login("user@example.com", "pass")
    # 버튼 CSS가 바뀌어도 LoginPage만 수정하면 됨
```

---

## 프로젝트 구조

```
pages/
├── __init__.py
├── base_page.py        # 공통 기능 (BasePage)
├── login_page.py       # 로그인 페이지
├── dashboard_page.py   # 대시보드
├── todo_page.py        # TodoMVC 예시
└── product_page.py     # 상품 목록/상세

tests/
├── conftest.py         # 픽스처 (page objects 생성)
└── 07_pom/
    └── test_pom.py
```

---

## BasePage 구현

> 📄 [`pages/base_page.py`](../pages/base_page.py)

```python
from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def navigate(self, url: str) -> None:
        self.page.goto(url)

    def reload(self) -> None:
        self.page.reload()

    @property
    def current_url(self) -> str:
        return self.page.url

    def take_screenshot(self, path: str) -> None:
        self.page.screenshot(path=path)
```

---

## Page Object 구현

> 📄 [`pages/todo_page.py`](../pages/todo_page.py)

```python
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class TodoPage(BasePage):
    URL = "https://demo.playwright.dev/todomvc"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # 셀렉터를 한 곳에서 관리
        self._input = page.get_by_role("textbox", name="What needs to be done?")
        self._todo_items = page.get_by_role("listitem")

    def open(self) -> "TodoPage":
        self.navigate(self.URL)
        return self

    def add_todo(self, text: str) -> "TodoPage":
        self._input.fill(text)
        self.page.keyboard.press("Enter")
        return self  # 메서드 체이닝 지원

    def complete_todo(self, text: str) -> "TodoPage":
        item = self._todo_items.filter(has_text=text)
        item.get_by_role("checkbox").click()
        return self

    # 단언 헬퍼
    def should_have_count(self, count: int) -> "TodoPage":
        expect(self._todo_items).to_have_count(count)
        return self
```

---

## conftest.py에서 픽스처 제공

```python
# conftest.py
import pytest
from playwright.sync_api import Page
from pages.todo_page import TodoPage
from pages.login_page import LoginPage


@pytest.fixture
def todo_page(page: Page) -> TodoPage:
    return TodoPage(page).open()


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page).open()
```

---

## 테스트 코드 — 비즈니스 언어

> 📄 [`tests/07_pom/test_pom.py`](../tests/07_pom/test_pom.py)

```python
def test_todo_workflow(self, todo_page: TodoPage) -> None:
    """비즈니스 시나리오를 그대로 표현합니다."""
    (
        todo_page
        .add_todos("아침 운동", "코드 리뷰", "E2E 테스트 작성")
        .complete_todo("아침 운동")
        .complete_todo("코드 리뷰")
        .filter_active()
        .should_have_count(1)
        .filter_completed()
        .should_have_count(2)
        .clear_completed()
        .filter_all()
        .should_have_count(1)
    )
```

---

## 실제 프로젝트 Page Object 예시

### LoginPage

```python
class LoginPage(BasePage):
    URL = "/login"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self._email = page.get_by_label("이메일")
        self._password = page.get_by_label("비밀번호")
        self._submit = page.get_by_role("button", name="로그인")
        self._error_msg = page.get_by_role("alert")

    def open(self) -> "LoginPage":
        self.navigate(f"{BASE_URL}{self.URL}")
        return self

    def login(self, email: str, password: str) -> None:
        self._email.fill(email)
        self._password.fill(password)
        self._submit.click()

    def should_show_error(self, message: str) -> "LoginPage":
        expect(self._error_msg).to_contain_text(message)
        return self
```

---

## 테스트 실행

```bash
uv run pytest tests/07_pom/ -v --headed
```

---

## POM 설계 원칙 정리

| 원칙 | 설명 |
|------|------|
| 셀렉터 캡슐화 | HTML 구조 변경 시 Page Object만 수정 |
| 메서드 체이닝 | `return self`로 유창한 API 제공 |
| 단언 헬퍼 | `should_` 접두사로 Page Object에 단언 포함 |
| 하나의 책임 | 각 Page는 하나의 페이지만 담당 |
| 상태 초기화 | `open()` 메서드로 진입점 명시 |

---

| 이전 | 다음 |
|------|------|
| [← 08. pytest 통합](./08-pytest-integration.md) | [10. E2E 테스트 전략 →](./10-e2e-strategy.md) |
