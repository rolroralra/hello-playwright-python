# 04. 사용자 액션

## 액션이란?

액션(Action)은 실제 사용자처럼 웹 페이지와 상호작용하는 동작입니다.
클릭, 입력, 스크롤, 키보드 조작 등이 포함됩니다.

---

## 페이지 이동

```python
# URL로 이동
page.goto("https://example.com")

# 이동 완료 조건 지정
page.goto("https://example.com", wait_until="load")        # 기본값
page.goto("https://example.com", wait_until="domcontentloaded")
page.goto("https://example.com", wait_until="networkidle") # 권장 (느릴 수 있음)

# 뒤로/앞으로
page.go_back()
page.go_forward()

# 새로고침
page.reload()
```

---

## 클릭

```python
# 기본 클릭
page.get_by_role("button", name="저장").click()

# 더블 클릭
page.get_by_text("항목").dblclick()

# 우클릭
page.get_by_text("항목").click(button="right")

# 특정 위치 클릭 (요소 내 상대 좌표)
page.locator(".card").click(position={"x": 10, "y": 5})

# 수정 키와 함께 클릭
page.get_by_role("link", name="열기").click(modifiers=["Control"])   # 새 탭
page.get_by_role("link", name="선택").click(modifiers=["Shift"])     # 다중 선택

# hover (마우스 올리기)
page.get_by_role("button", name="메뉴").hover()

# focus (포커스)
page.get_by_role("textbox").focus()
```

---

## 텍스트 입력

### fill() vs press_sequentially()

| 메서드 | 동작 | 사용 상황 |
|--------|------|-----------|
| `fill(text)` | 내용을 즉시 교체 | 일반적인 경우 (빠름) |
| `press_sequentially(text)` | 한 글자씩 키 입력 | 자동완성, 실시간 이벤트 필요 시 |

```python
# fill: 빠르고 직접적
page.get_by_label("이메일").fill("user@example.com")

# press_sequentially: 실제 타이핑처럼 (delay 옵션으로 속도 조절)
page.get_by_label("검색").press_sequentially("Playwright", delay=50)

# 내용 지우기
page.get_by_label("이름").clear()

# 내용 확인
value = page.get_by_label("이름").input_value()
```

---

## 키보드

```python
# 특정 키 누르기
page.keyboard.press("Enter")
page.keyboard.press("Tab")
page.keyboard.press("Escape")
page.keyboard.press("ArrowDown")

# 단축키 (조합키)
page.keyboard.press("Control+a")   # 전체 선택
page.keyboard.press("Control+c")   # 복사
page.keyboard.press("Control+v")   # 붙여넣기
page.keyboard.press("Meta+a")      # macOS: Cmd+A

# 요소에서 키 누르기
page.get_by_role("textbox").press("Enter")

# 키 누르고 있기 / 떼기
page.keyboard.down("Shift")
page.keyboard.up("Shift")
```

---

## 폼 요소

```python
# 체크박스
page.get_by_role("checkbox", name="동의").check()
page.get_by_role("checkbox", name="동의").uncheck()
page.get_by_role("checkbox", name="동의").set_checked(True)

# 라디오 버튼
page.get_by_role("radio", name="남성").check()

# 드롭다운 선택
page.get_by_role("combobox", name="국가").select_option("KR")         # value
page.get_by_role("combobox", name="국가").select_option(label="Korea") # label
page.get_by_role("combobox", name="국가").select_option(index=2)       # index

# 파일 업로드
page.get_by_label("파일 선택").set_input_files("path/to/file.pdf")

# 다중 파일 업로드
page.get_by_label("파일").set_input_files(["file1.pdf", "file2.pdf"])
```

---

## 스크롤

```python
# 페이지 스크롤
page.mouse.wheel(0, 300)   # (delta_x, delta_y)

# 요소가 보이도록 스크롤
page.get_by_text("맨 아래 내용").scroll_into_view_if_needed()

# 요소 내부 스크롤
page.locator(".scrollable-list").evaluate("el => el.scrollTop = 100")
```

---

## 실습 코드

> 📄 [`tests/03_actions/test_actions.py`](../tests/03_actions/test_actions.py)

### TodoMVC 전체 워크플로우

```python
def test_add_and_complete_todo(self, todo_page: Page) -> None:
    input_box = todo_page.get_by_role("textbox", name="What needs to be done?")

    for task in ["Buy milk", "Walk the dog", "Read a book"]:
        input_box.fill(task)
        todo_page.keyboard.press("Enter")

    expect(todo_page.get_by_role("listitem")).to_have_count(3)

    # 첫 번째 완료 처리
    todo_page.get_by_role("listitem").first.get_by_role("checkbox").click()

    # Active 필터 → 2개
    todo_page.get_by_role("link", name="Active").click()
    expect(todo_page.get_by_role("listitem")).to_have_count(2)
```

---

## 테스트 실행

```bash
pytest tests/03_actions/ -v --headed
```

---

## Auto-waiting 이해하기

Playwright는 대부분의 액션에서 **자동으로 대기**합니다.

```python
# 이 코드는 버튼이 나타날 때까지 자동 대기
page.get_by_role("button", name="저장").click()
```

내부적으로 수행하는 검사:
1. 요소가 DOM에 존재하는지
2. 요소가 화면에 보이는지 (visible)
3. 요소가 stable한 상태인지 (애니메이션 완료)
4. 요소가 enabled 상태인지
5. 요소가 클릭 가능한 위치에 있는지

> 다음 챕터에서 대기 전략을 더 자세히 다룹니다.

---

| 이전 | 다음 |
|------|------|
| [← 03. 셀렉터](./03-selectors.md) | [05. 단언(Assertions) →](./05-assertions.md) |
