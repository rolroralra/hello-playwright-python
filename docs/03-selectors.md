# 03. 셀렉터 (요소 탐색)

## 셀렉터란?

셀렉터(Selector)는 웹 페이지에서 특정 HTML 요소를 찾는 방법입니다.
Playwright는 여러 종류의 셀렉터를 지원하며, **권장 우선순위**가 있습니다.

```
권장 순서:
1. get_by_role()     ← 접근성 기반, 가장 권장
2. get_by_text()     ← 텍스트 기반
3. get_by_label()    ← 폼 레이블 기반
4. get_by_placeholder()
5. get_by_test_id()  ← data-testid 속성
6. locator("css")    ← CSS 셀렉터
7. locator("xpath")  ← XPath (마지막 수단)
```

> **왜 role이 권장될까요?**
> - 구현(HTML 구조)이 바뀌어도 역할(role)은 변하지 않는 경우가 많습니다.
> - 접근성(a11y) 기준과 동일하게 동작합니다.
> - 테스트가 실제 사용자 관점을 반영합니다.

---

## get_by_role() — 역할 기반 탐색

```python
# 텍스트박스 (input type=text, textarea 등)
page.get_by_role("textbox", name="이름")

# 버튼
page.get_by_role("button", name="저장")

# 링크
page.get_by_role("link", name="Docs")

# 체크박스
page.get_by_role("checkbox", name="동의합니다")

# 제목
page.get_by_role("heading", name="회원가입")

# 목록 항목
page.get_by_role("listitem")

# 테이블 행
page.get_by_role("row")
```

### 자주 쓰이는 role 값

| role | 해당 HTML 요소 |
|------|----------------|
| `button` | `<button>`, `type="button"` |
| `link` | `<a href="...">` |
| `textbox` | `<input type="text">`, `<textarea>` |
| `checkbox` | `<input type="checkbox">` |
| `radio` | `<input type="radio">` |
| `heading` | `<h1>` ~ `<h6>` |
| `listitem` | `<li>` |
| `row` | `<tr>` |
| `cell` | `<td>` |
| `combobox` | `<select>` |
| `img` | `<img>` |

---

## get_by_text() — 텍스트 기반 탐색

```python
# 정확히 일치
page.get_by_text("저장하기", exact=True)

# 부분 일치 (기본값)
page.get_by_text("저장")

# 대소문자 무시
import re
page.get_by_text(re.compile("저장", re.IGNORECASE))
```

---

## get_by_label() / get_by_placeholder()

```python
# <label>과 연결된 input 찾기
page.get_by_label("이메일")

# placeholder 속성으로 찾기
page.get_by_placeholder("이메일을 입력하세요")
```

---

## locator() — CSS / XPath

```python
# CSS 클래스
page.locator(".submit-button")

# CSS ID
page.locator("#username")

# CSS 복합 선택자
page.locator("ul.todo-list > li")

# XPath
page.locator("//button[text()='저장']")
page.locator("xpath=//div[@class='card']")
```

---

## 로케이터 체이닝 — 범위 좁히기

```python
# 특정 컨테이너 안에서만 탐색
sidebar = page.locator(".sidebar")
sidebar.get_by_role("link", name="대시보드")

# filter()로 조건 필터링
page.get_by_role("listitem").filter(has_text="구매 완료")

# n번째 요소 선택
items = page.get_by_role("listitem")
items.first       # 첫 번째
items.last        # 마지막
items.nth(2)      # 세 번째 (0-indexed)
```

---

## 실습 코드

> 📄 [`tests/02_selectors/test_selectors.py`](../tests/02_selectors/test_selectors.py)

### Role 셀렉터 실습

```python
def test_get_by_role_textbox(self, todo_page: Page) -> None:
    input_box = todo_page.get_by_role("textbox", name="What needs to be done?")
    expect(input_box).to_be_visible()
```

### 로케이터 체이닝 실습

```python
def test_filter_by_text(self, todo_page: Page) -> None:
    # 할 일 두 개 추가
    input_box = todo_page.get_by_role("textbox", name="What needs to be done?")
    input_box.fill("Buy milk")
    todo_page.keyboard.press("Enter")
    input_box.fill("Buy eggs")
    todo_page.keyboard.press("Enter")

    # 'Buy milk' 항목만 필터링
    milk_item = todo_page.get_by_role("listitem").filter(has_text="Buy milk")
    expect(milk_item).to_have_count(1)
```

---

## 테스트 실행

```bash
uv run pytest tests/02_selectors/ -v --headed
```

---

## 셀렉터 선택 가이드

```
Q: 폼 요소(input, textarea, select)를 찾을 때?
A: get_by_label() 또는 get_by_role("textbox", name="...")

Q: 버튼을 찾을 때?
A: get_by_role("button", name="저장")

Q: 링크를 찾을 때?
A: get_by_role("link", name="로그인")

Q: 특정 텍스트를 가진 요소?
A: get_by_text("...")

Q: 백엔드에서 data-testid를 내려준다면?
A: get_by_test_id("submit-btn")

Q: 위 방법이 모두 불가능하다면?
A: locator(".css-class") → locator("//xpath")
```

---

| 이전 | 다음 |
|------|------|
| [← 02. 첫 번째 테스트](./02-first-test.md) | [04. 사용자 액션 →](./04-actions.md) |
