# 08. pytest 통합

## pytest-playwright 픽스처 체계

`pytest-playwright`는 pytest의 픽스처(fixture) 시스템을 통해 브라우저 생명주기를 관리합니다.

```
session 스코프
  └── playwright (Playwright 인스턴스)
        └── browser (Browser 인스턴스)
              └── browser_context (function 스코프, 테스트마다 새로 생성)
                    └── page (function 스코프, 테스트마다 새로 생성)
```

---

## conftest.py — 공통 픽스처

```python
# conftest.py
import pytest
from playwright.sync_api import Page, Playwright, APIRequestContext

BASE_URL = "https://myapp.com"
API_BASE_URL = "https://api.myapp.com"


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.fixture(scope="session")
def api_context(playwright: Playwright) -> APIRequestContext:
    """세션 전체에서 재사용하는 API 컨텍스트."""
    context = playwright.request.new_context(
        base_url=API_BASE_URL,
        extra_http_headers={
            "Authorization": "Bearer test_token",
        },
    )
    yield context
    context.dispose()


@pytest.fixture
def logged_in_page(page: Page, base_url: str) -> Page:
    """로그인된 상태의 page 픽스처."""
    page.goto(f"{base_url}/login")
    page.get_by_label("이메일").fill("test@example.com")
    page.get_by_label("비밀번호").fill("password123")
    page.get_by_role("button", name="로그인").click()
    page.wait_for_url(f"{base_url}/dashboard")
    return page
```

---

## 픽스처 스코프

| 스코프 | 생명주기 | 사용 상황 |
|--------|----------|-----------|
| `function` | 각 테스트마다 | 기본값, 격리가 필요할 때 |
| `class` | 클래스 내 공유 | 같은 클래스의 테스트가 상태 공유 |
| `module` | 모듈(파일) 내 공유 | 파일 단위로 셋업 필요 |
| `session` | 전체 세션 공유 | API 컨텍스트, 브라우저 인스턴스 |

```python
@pytest.fixture(scope="class")
def setup_data(page: Page) -> dict:
    """같은 클래스의 테스트가 공유하는 데이터."""
    # 한 번만 실행
    return {"user_id": 1, "token": "abc123"}
```

---

## pytest 마커

`pytest.ini`에 마커를 정의하고 테스트를 그룹화합니다.

```ini
# pytest.ini
[pytest]
markers =
    smoke: 핵심 시나리오 (빠른 검증)
    regression: 전체 회귀 테스트
    api: API 레이어 테스트
    ui: UI 레이어 테스트
    e2e: 엔드투엔드 시나리오
```

```python
import pytest

@pytest.mark.smoke
@pytest.mark.ui
def test_login_page_loads(page: Page) -> None:
    ...

@pytest.mark.api
def test_user_api(api: APIRequestContext) -> None:
    ...
```

```bash
# 마커로 선택 실행
pytest -m smoke
pytest -m "api and not slow"
pytest -m "e2e or regression"
```

---

## 파라미터화

```python
import pytest

@pytest.mark.parametrize("browser_name", ["chromium", "firefox", "webkit"])
def test_cross_browser(browser_name: str, playwright) -> None:
    browser = getattr(playwright, browser_name).launch()
    page = browser.new_page()
    page.goto("https://playwright.dev")
    assert "Playwright" in page.title()
    browser.close()


@pytest.mark.parametrize(
    "username, password, expected",
    [
        ("admin", "correct", "dashboard"),
        ("admin", "wrong", "login"),
        ("", "", "login"),
    ],
)
def test_login_scenarios(page: Page, username: str, password: str, expected: str) -> None:
    page.goto("https://myapp.com/login")
    page.get_by_label("이메일").fill(username)
    page.get_by_label("비밀번호").fill(password)
    page.get_by_role("button", name="로그인").click()
    assert expected in page.url
```

---

## 브라우저 옵션 설정

### 전역 설정 (pytest.ini)

```ini
[pytest]
# 기본 브라우저
addopts = --browser chromium

# 헤드리스 OFF
# addopts = --headed

# 느리게 실행
# addopts = --headed --slowmo 500

# 비디오 녹화
# addopts = --video=on

# 트레이스 수집
# addopts = --tracing=on
```

### 커맨드라인 옵션

```bash
pytest --browser chromium       # 브라우저 선택
pytest --browser firefox
pytest --browser webkit

pytest --headed                  # 브라우저 화면 표시
pytest --slowmo 500              # 500ms 지연

pytest --video=on                # 비디오 녹화
pytest --tracing=on              # 트레이스 수집

pytest --screenshot=on           # 스크린샷 (실패 시)
pytest --screenshot=only-on-failure

pytest --output=test-results     # 출력 디렉토리
```

---

## 비디오 & 트레이스

```bash
# 비디오 녹화
pytest --video=on --output=test-results

# 트레이스 수집 (Playwright Trace Viewer로 분석)
pytest --tracing=on --output=test-results

# 트레이스 뷰어 열기
playwright show-trace test-results/trace.zip
```

---

## HTML 리포트

```bash
pip install pytest-html

# 리포트 생성
pytest --html=reports/report.html --self-contained-html
```

---

## 병렬 실행

```bash
pip install pytest-xdist

# 4개 프로세스로 병렬 실행
pytest -n 4

# CPU 수만큼 자동 설정
pytest -n auto
```

---

| 이전 | 다음 |
|------|------|
| [← 07. API 테스팅](./07-api-testing.md) | [09. Page Object Model →](./09-page-object-model.md) |
