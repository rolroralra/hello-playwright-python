# 02. 첫 번째 테스트 작성

## pytest-playwright 플러그인 이해하기

`pytest-playwright`를 설치하면 pytest 플러그인이 자동으로 등록됩니다.
별도 코드 없이 **`page`, `browser`, `context` 픽스처**를 바로 사용할 수 있습니다.

```python
# 이것만으로 충분 — 설정 코드 없음!
from playwright.sync_api import Page

def test_example(page: Page) -> None:
    page.goto("https://example.com")
```

---

## 기본 테스트 구조

```python
from playwright.sync_api import Page, expect


def test_page_title(page: Page) -> None:
    # 1. 페이지 이동
    page.goto("https://playwright.dev")

    # 2. 단언(Assertion)
    expect(page).to_have_title("Fast and reliable end-to-end testing for modern web apps | Playwright")
```

### 핵심 패턴

| 단계 | 코드 | 설명 |
|------|------|------|
| 이동 | `page.goto(url)` | 특정 URL로 이동 |
| 찾기 | `page.get_by_role(...)` | 요소 탐색 |
| 행동 | `.click()`, `.fill()` | 사용자 행동 |
| 단언 | `expect(...).to_...()` | 결과 검증 |

---

## pytest-playwright가 제공하는 기본 픽스처

| 픽스처 | 스코프 | 설명 |
|--------|--------|------|
| `playwright` | session | Playwright 인스턴스 |
| `browser` | session | 브라우저 인스턴스 |
| `browser_context` | function | BrowserContext (테스트마다 새로 생성) |
| `page` | function | Page (테스트마다 새로 생성) |

```python
def test_using_context(browser_context, page: Page) -> None:
    # browser_context: 쿠키, 로컬스토리지 접근 가능
    # page: 실제 탭
    pass
```

---

## 실습 코드

> 📄 [`tests/01_basic/test_first_playwright.py`](../tests/01_basic/test_first_playwright.py)

### 테스트 1: 페이지 타이틀 확인

```python
def test_page_title(self, page: Page) -> None:
    page.goto("https://playwright.dev")
    expect(page).to_have_title(
        "Fast and reliable end-to-end testing for modern web apps | Playwright"
    )
```

### 테스트 2: 링크 클릭 후 URL 확인

```python
def test_navigate_to_docs(self, page: Page) -> None:
    page.goto("https://playwright.dev")
    page.get_by_role("link", name="Docs").click()
    expect(page).to_have_url("https://playwright.dev/docs/intro")
```

### 테스트 3: BrowserContext 격리

```python
def test_browser_context_isolation(self, browser) -> None:
    context1 = browser.new_context()
    page1 = context1.new_page()
    page1.goto("https://playwright.dev")

    context2 = browser.new_context()
    page2 = context2.new_page()
    page2.goto("https://playwright.dev")

    expect(page1).to_have_url("https://playwright.dev/")
    expect(page2).to_have_url("https://playwright.dev/")

    context1.close()
    context2.close()
```

> `BrowserContext`는 각자 독립된 세션을 가집니다. 로그인 상태가 다른 두 사용자를 동시에 테스트할 때 유용합니다.

---

## 테스트 실행

```bash
# 전체 실행
uv run pytest tests/01_basic/ -v

# 브라우저 화면 보기
uv run pytest tests/01_basic/ -v --headed

# 특정 테스트만 실행
uv run pytest tests/01_basic/test_first_playwright.py::TestFirstPlaywright::test_page_title -v

# Firefox로 실행
uv run pytest tests/01_basic/ -v --browser firefox
```

### 실행 결과 예시

```
tests/01_basic/test_first_playwright.py::TestFirstPlaywright::test_page_title PASSED
tests/01_basic/test_first_playwright.py::TestFirstPlaywright::test_page_url PASSED
tests/01_basic/test_first_playwright.py::TestFirstPlaywright::test_navigate_to_docs PASSED
tests/01_basic/test_first_playwright.py::TestFirstPlaywright::test_browser_context_isolation PASSED
tests/01_basic/test_first_playwright.py::TestFirstPlaywright::test_screenshot PASSED
tests/01_basic/test_first_playwright.py::TestFirstPlaywright::test_viewport_size PASSED
```

---

## 디버깅 팁

### Inspector 실행

```bash
# Playwright Inspector GUI 실행
PWDEBUG=1 uv run pytest tests/01_basic/ --headed
```

### 코드 생성기 (Codegen)

브라우저를 직접 조작하면서 코드를 자동 생성해주는 도구입니다.
실행하면 브라우저 창과 Playwright Inspector 창이 함께 열리고, 클릭/입력 등의 동작이 실시간으로 코드로 기록됩니다.

```bash
# 기본 실행 (Python 동기 API 코드 생성)
uv run playwright codegen https://playwright.dev

# pytest 형식으로 생성
uv run playwright codegen --target python-pytest https://demo.playwright.dev/todomvc

# 생성된 코드를 파일로 저장
uv run playwright codegen --target python-pytest -o tests/test_generated.py https://demo.playwright.dev/todomvc
```

#### 자주 쓰는 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--target` | 생성할 코드 형식 (`python`, `python-async`, `python-pytest` 등) | `--target python-pytest` |
| `-o, --output` | 생성된 코드를 파일로 저장 | `-o tests/test_generated.py` |
| `-b, --browser` | 브라우저 선택 (`chromium`, `firefox`, `webkit`) | `-b webkit` |
| `--device` | 모바일 기기 에뮬레이션 | `--device "iPhone 13"` |
| `--viewport-size` | 뷰포트 크기 지정 | `--viewport-size "1280,720"` |
| `--save-storage` | 종료 시 쿠키/로컬스토리지 상태 저장 | `--save-storage auth.json` |
| `--load-storage` | 저장된 상태를 불러와 시작 (로그인 상태 재사용) | `--load-storage auth.json` |
| `--test-id-attribute` | 테스트 ID로 사용할 속성 지정 | `--test-id-attribute data-qa` |

#### 로그인 상태 재사용 예시

```bash
# 1. 로그인까지 직접 진행한 뒤 창을 닫으면 auth.json에 상태가 저장됨
uv run playwright codegen --save-storage auth.json https://example.com/login

# 2. 저장된 로그인 상태로 바로 기록 시작
uv run playwright codegen --load-storage auth.json https://example.com/dashboard
```

> **주의**: Codegen이 만든 코드는 출발점일 뿐입니다. 생성된 셀렉터를 `get_by_role()` 같은 의미 기반 로케이터로 다듬고([03. 셀렉터](./03-selectors.md) 참고), 단언(`expect`)을 직접 추가해야 테스트로서 의미가 있습니다.
> `auth.json`에는 세션 쿠키가 들어 있으므로 `.gitignore`에 추가하세요.

전체 옵션은 `uv run playwright codegen --help`로 확인할 수 있습니다.

---

| 이전 | 다음 |
|------|------|
| [← 01. 소개 및 환경 설정](./01-introduction.md) | [03. 셀렉터(요소 탐색) →](./03-selectors.md) |
