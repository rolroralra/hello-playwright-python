# 05. 단언 (Assertions)

## expect() API

Playwright의 `expect()` 함수는 **Auto-retrying Assertion**을 제공합니다.
조건이 충족될 때까지 기본 5초 동안 재시도하므로, 타이밍 이슈를 걱정하지 않아도 됩니다.

```python
from playwright.sync_api import expect

# 5초 내에 조건이 충족되면 통과, 그렇지 않으면 실패
expect(page.get_by_role("button")).to_be_visible()
```

> **Auto-retrying vs assert**
> ```python
> # ❌ 이렇게 하면 안 됨 — 타이밍 이슈 발생 가능
> assert page.get_by_role("button").is_visible()
>
> # ✅ 이렇게 해야 함 — 내부적으로 재시도
> expect(page.get_by_role("button")).to_be_visible()
> ```

---

## Page 단언

```python
# 타이틀
expect(page).to_have_title("홈 페이지")
expect(page).to_have_title(re.compile(r"홈"))

# URL
expect(page).to_have_url("https://example.com/")
expect(page).to_have_url(re.compile(r"/dashboard"))
```

---

## 가시성 단언

```python
# 보이는지
expect(locator).to_be_visible()

# 숨겨져 있는지
expect(locator).to_be_hidden()

# 부정 (not_to_)
expect(locator).not_to_be_visible()
```

---

## 텍스트 단언

```python
# 정확히 일치
expect(locator).to_have_text("정확한 텍스트")

# 부분 포함
expect(locator).to_contain_text("일부 텍스트")

# 정규식
expect(locator).to_have_text(re.compile(r"패턴"))

# 여러 요소의 텍스트 목록
expect(page.get_by_role("listitem")).to_have_text(["항목1", "항목2", "항목3"])
```

---

## 카운트 단언

```python
# 개수 확인
expect(page.get_by_role("listitem")).to_have_count(3)
expect(page.get_by_role("listitem")).not_to_have_count(0)
```

---

## 상태 단언

```python
# 활성화/비활성화
expect(locator).to_be_enabled()
expect(locator).to_be_disabled()

# 체크박스 상태
expect(checkbox).to_be_checked()
expect(checkbox).not_to_be_checked()

# 포커스
expect(locator).to_be_focused()

# 비어 있는지 (input)
expect(input).to_be_empty()
```

---

## 속성 / 값 단언

```python
# HTML 속성
expect(link).to_have_attribute("href", "/docs")
expect(img).to_have_attribute("alt", "로고")

# CSS 클래스
expect(element).to_have_class("active")
expect(element).to_have_class(re.compile("btn-"))

# input 값
expect(input).to_have_value("입력된 값")

# CSS 속성값
expect(element).to_have_css("color", "rgb(255, 0, 0)")
```

---

## Soft Assertions

기본적으로 단언이 실패하면 테스트가 즉시 중단됩니다.
`expect.soft()`를 사용하면 실패를 기록하되 계속 진행합니다.

```python
def test_multiple_checks(page: Page) -> None:
    page.goto("https://playwright.dev")

    # 실패해도 계속 진행
    expect.soft(page).to_have_title("Playwright")
    expect.soft(page.get_by_role("link", name="Docs")).to_be_visible()
    expect.soft(page.get_by_role("link", name="API")).to_be_visible()

    # 모든 soft assertion 실패가 마지막에 보고됨
```

---

## Timeout 커스터마이징

```python
# 기본 5초 → 10초로 변경
expect(locator).to_be_visible(timeout=10_000)

# 빠른 체크 (1초)
expect(locator).to_be_hidden(timeout=1_000)
```

---

## 실습 코드

> 📄 [`tests/04_assertions/test_assertions.py`](../tests/04_assertions/test_assertions.py)

### 텍스트 목록 단언

```python
def test_multiple_items_text(self, todo_page: Page) -> None:
    input_box = todo_page.get_by_role("textbox", name="What needs to be done?")
    for task in ["Task A", "Task B", "Task C"]:
        input_box.fill(task)
        todo_page.keyboard.press("Enter")

    # 순서대로 텍스트 확인
    expect(todo_page.get_by_role("listitem")).to_have_text(
        ["Task A", "Task B", "Task C"]
    )
```

### 상태 변화 단언

```python
def test_to_be_checked(self, todo_page: Page) -> None:
    todo_page.get_by_role("textbox", name="What needs to be done?").fill("Task")
    todo_page.keyboard.press("Enter")

    checkbox = todo_page.get_by_role("listitem").first.get_by_role("checkbox")

    expect(checkbox).not_to_be_checked()  # 초기 상태

    checkbox.click()

    expect(checkbox).to_be_checked()  # 클릭 후
```

---

## 테스트 실행

```bash
uv run pytest tests/04_assertions/ -v --headed
```

---

## 단언 전체 목록 (요약)

| 단언 | 설명 |
|------|------|
| `to_be_visible()` | 화면에 보임 |
| `to_be_hidden()` | 숨겨짐 |
| `to_be_enabled()` | 활성화 |
| `to_be_disabled()` | 비활성화 |
| `to_be_checked()` | 체크됨 |
| `to_be_empty()` | 빈 입력 |
| `to_be_focused()` | 포커스됨 |
| `to_have_text(text)` | 텍스트 일치 |
| `to_contain_text(text)` | 텍스트 포함 |
| `to_have_count(n)` | 개수 확인 |
| `to_have_value(val)` | input 값 |
| `to_have_attribute(k, v)` | 속성 확인 |
| `to_have_class(cls)` | CSS 클래스 |
| `to_have_url(url)` | URL 확인 |
| `to_have_title(title)` | 타이틀 확인 |

---

| 이전 | 다음 |
|------|------|
| [← 04. 사용자 액션](./04-actions.md) | [06. 대기 전략 & 네트워크 →](./06-waiting-and-network.md) |
