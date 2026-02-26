# 06. 대기 전략 & 네트워크

## Auto-waiting

Playwright는 대부분의 액션에서 **자동으로 대기**합니다.
별도의 `time.sleep()` 없이도 안정적인 테스트 작성이 가능합니다.

### Auto-waiting이 확인하는 조건

```
click() 호출 시 내부 동작:
  1. 요소가 DOM에 존재하는가?
  2. 요소가 visible 상태인가?
  3. 요소가 stable 상태인가? (애니메이션 완료)
  4. 요소가 enabled 상태인가?
  5. 요소가 클릭 가능한 위치에 있는가?
```

```python
# ❌ 나쁜 예시: sleep으로 기다리기
import time
time.sleep(2)
page.get_by_role("button", name="저장").click()

# ✅ 좋은 예시: Playwright가 자동으로 대기
page.get_by_role("button", name="저장").click()  # 이미 안전
```

---

## 페이지 로드 대기

```python
# 기본: load (모든 리소스 로드 완료)
page.goto("https://example.com")
page.goto("https://example.com", wait_until="load")

# DOM 파싱만 완료
page.goto("https://example.com", wait_until="domcontentloaded")

# 네트워크 요청이 없을 때 (SPA에서 유용)
page.goto("https://example.com", wait_until="networkidle")

# 이동 후 명시적으로 상태 기다리기
page.goto("https://example.com")
page.wait_for_load_state("networkidle")
```

---

## URL 대기

```python
# 특정 URL로 변경될 때까지 대기
page.wait_for_url("https://example.com/dashboard")

# 정규식 패턴
import re
page.wait_for_url(re.compile(r"/dashboard"))

# glob 패턴
page.wait_for_url("**/dashboard**")
```

---

## 셀렉터 대기

```python
# 요소가 나타날 때까지 대기 (기본: visible 상태)
page.wait_for_selector(".loading-spinner", state="hidden")  # 사라질 때까지
page.wait_for_selector(".result-list", state="visible")      # 나타날 때까지
page.wait_for_selector(".item", state="attached")            # DOM에 존재할 때까지
```

---

## JavaScript 조건 대기

```python
# JS 함수가 true를 반환할 때까지 대기
page.wait_for_function("window.dataLoaded === true")
page.wait_for_function("document.readyState === 'complete'")

# 인자 전달
page.wait_for_function(
    "count => document.querySelectorAll('li').length >= count",
    arg=3
)
```

---

## 명시적 시간 대기

```python
# 500ms 대기
# ⚠️ 최후의 수단으로만 사용 — flaky test의 주범
page.wait_for_timeout(500)
```

---

## 네트워크 인터셉트 (route)

네트워크 요청을 가로채서 차단, 수정, 모킹할 수 있습니다.
테스트 격리와 속도 향상에 매우 유용합니다.

### 요청 차단

```python
# 이미지 요청 차단 (테스트 속도 향상)
page.route("**/*.png", lambda route: route.abort())
page.route("**/*.jpg", lambda route: route.abort())

# 광고/분석 요청 차단
page.route("**/analytics.js", lambda route: route.abort())
```

### API 응답 모킹

```python
import json

mock_users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

page.route(
    "**/api/users",
    lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body=json.dumps(mock_users),
    )
)

page.goto("https://myapp.com/users")
# API 응답이 mock_users로 대체됨
```

### 응답 수정 (원본 요청 유지 + 내용만 변경)

```python
def handle_route(route: Route) -> None:
    response = route.fetch()       # 원래 요청 실행
    data = response.json()         # 응답 파싱
    data["extra_field"] = "추가"  # 데이터 수정
    route.fulfill(response=response, json=data)  # 수정된 응답 반환

page.route("**/api/user/profile", handle_route)
```

---

## 네트워크 이벤트 감지

```python
# 요청 캡처
requests = []
page.on("request", lambda req: requests.append(req))
page.goto("https://example.com")
print(f"총 {len(requests)}개 요청 발생")

# 특정 응답 기다리기
with page.expect_response("**/api/data") as response_info:
    page.get_by_role("button", name="데이터 로드").click()

response = response_info.value
assert response.status == 200
data = response.json()

# 특정 요청 기다리기
with page.expect_request("**/api/submit") as request_info:
    page.get_by_role("button", name="제출").click()

request = request_info.value
body = request.post_data_json()
assert body["name"] == "테스트"
```

---

## 실습 코드

> 📄 [`tests/05_waiting/test_waiting_and_network.py`](../tests/05_waiting/test_waiting_and_network.py)

### API 응답 모킹 실습

```python
def test_route_mock_response(self, page: Page) -> None:
    mock_data = {"id": 1, "title": "Mock Todo Item", "completed": False}

    page.route(
        "https://jsonplaceholder.typicode.com/todos/1",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_data),
        ),
    )

    response = page.evaluate("""
        async () => {
            const res = await fetch('https://jsonplaceholder.typicode.com/todos/1');
            return res.json();
        }
    """)

    assert response["title"] == "Mock Todo Item"
```

---

## 테스트 실행

```bash
pytest tests/05_waiting/ -v --headed
```

---

## 대기 전략 결정 흐름

```
요소를 기다려야 한다면?
    └─ Auto-waiting으로 충분한가?
           ├─ YES: 그냥 사용 (click, fill 등)
           └─ NO: 어떤 상태를 기다려야 하는가?
                  ├─ URL 변경: wait_for_url()
                  ├─ 로드 완료: wait_for_load_state()
                  ├─ 요소 등장: wait_for_selector()
                  ├─ JS 조건: wait_for_function()
                  └─ 시간: wait_for_timeout() ← 최후의 수단
```

---

| 이전 | 다음 |
|------|------|
| [← 05. 단언(Assertions)](./05-assertions.md) | [07. API 테스팅 →](./07-api-testing.md) |
