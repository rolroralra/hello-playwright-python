# 07. API 테스팅

## Playwright로 API 테스트하기

Playwright는 UI 자동화뿐만 아니라 **HTTP API 테스트**도 지원합니다.
`APIRequestContext`를 사용해 REST API를 직접 호출할 수 있습니다.

### 서버 개발자에게 왜 중요한가?

```
서버 개발자의 테스트 흐름:
  1. API 단위 테스트 (JUnit, pytest 등)
  2. API 통합 테스트 ← APIRequestContext 활용
  3. E2E 테스트 (UI + API 결합)
```

Playwright의 API 테스트 기능을 사용하면:
- 동일한 도구(pytest + playwright)로 API와 UI 테스트 통합
- UI 테스트 전 API로 데이터 준비 (빠른 셋업)
- UI 액션 후 API로 백엔드 상태 검증

---

## APIRequestContext 설정

```python
import pytest
from playwright.sync_api import Playwright, APIRequestContext


@pytest.fixture(scope="session")
def api_request_context(playwright: Playwright) -> APIRequestContext:
    context = playwright.request.new_context(
        base_url="https://api.example.com",
        extra_http_headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer YOUR_TOKEN",  # 인증 토큰
        },
    )
    yield context
    context.dispose()
```

---

## HTTP 메서드

### GET

```python
def test_get_list(self, api: APIRequestContext) -> None:
    response = api.get("/users")

    assert response.status == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) > 0

def test_get_with_params(self, api: APIRequestContext) -> None:
    response = api.get(
        "/users",
        params={"role": "admin", "active": "true"},
    )
    assert response.status == 200
```

### POST

```python
def test_create_user(self, api: APIRequestContext) -> None:
    new_user = {
        "name": "홍길동",
        "email": "hong@example.com",
        "role": "user",
    }

    response = api.post("/users", data=new_user)

    assert response.status == 201
    created = response.json()
    assert created["email"] == new_user["email"]
    assert "id" in created
```

### PUT / PATCH

```python
# PUT: 전체 교체
response = api.put("/users/1", data={"name": "변경된 이름", ...})

# PATCH: 부분 업데이트
response = api.patch("/users/1", data={"name": "변경된 이름"})
assert response.status == 200
```

### DELETE

```python
def test_delete_user(self, api: APIRequestContext) -> None:
    response = api.delete("/users/1")
    assert response.status in [200, 204]  # 삭제 성공
```

---

## 응답 처리

```python
response = api.get("/users/1")

# 상태 코드
status = response.status          # 200
status_text = response.status_text # "OK"

# 바디
json_data = response.json()        # dict
text_data = response.text()        # str
bytes_data = response.body()       # bytes

# 헤더
content_type = response.headers["content-type"]
all_headers = response.headers     # dict

# 성공 여부
response.ok   # status < 400이면 True
```

---

## 인증 처리

### Bearer Token

```python
@pytest.fixture(scope="session")
def authenticated_api(playwright: Playwright) -> APIRequestContext:
    # 먼저 로그인 API로 토큰 획득
    context = playwright.request.new_context(
        base_url="https://api.example.com"
    )

    login_response = context.post(
        "/auth/login",
        data={"username": "admin", "password": "password"},
    )
    token = login_response.json()["access_token"]
    context.dispose()

    # 토큰을 헤더에 포함한 새 컨텍스트 생성
    return playwright.request.new_context(
        base_url="https://api.example.com",
        extra_http_headers={"Authorization": f"Bearer {token}"},
    )
```

### Cookie 기반

```python
@pytest.fixture(scope="session")
def cookie_authenticated_api(playwright: Playwright) -> APIRequestContext:
    context = playwright.request.new_context(
        base_url="https://api.example.com"
    )

    # 로그인 (서버가 Set-Cookie로 세션 쿠키를 내려줌)
    context.post("/auth/login", data={"username": "admin", "password": "pass"})

    # 이후 요청에 쿠키가 자동으로 포함됨
    return context
```

---

## UI + API 결합 패턴

서버 개발자에게 가장 실용적인 패턴입니다.

### 패턴 1: API로 셋업 → UI로 검증

```python
def test_api_setup_then_verify_ui(self, page: Page, playwright: Playwright) -> None:
    # Step 1: API로 테스트 데이터 생성 (빠름)
    api = playwright.request.new_context(base_url="https://api.example.com")
    response = api.post("/products", data={"name": "테스트 상품", "price": 1000})
    product_id = response.json()["id"]
    api.dispose()

    # Step 2: UI에서 해당 데이터 검증
    page.goto(f"https://myapp.com/products/{product_id}")
    expect(page.get_by_role("heading")).to_contain_text("테스트 상품")
    expect(page.get_by_text("1,000원")).to_be_visible()
```

### 패턴 2: UI 액션 → API로 검증

```python
def test_ui_submit_then_verify_api(self, page: Page, playwright: Playwright) -> None:
    # Step 1: UI에서 주문 생성
    page.goto("https://myapp.com/order")
    page.get_by_label("상품명").fill("커피")
    page.get_by_label("수량").fill("2")
    page.get_by_role("button", name="주문").click()

    # Step 2: API로 실제 저장됐는지 검증
    api = playwright.request.new_context(base_url="https://api.example.com")
    response = api.get("/orders?latest=1")
    order = response.json()[0]
    assert order["product"] == "커피"
    assert order["quantity"] == 2
    api.dispose()
```

---

## 실습 코드

> 📄 [`tests/06_api/test_api_testing.py`](../tests/06_api/test_api_testing.py)

### 전체 CRUD 테스트

```python
def test_create_todo(self, api_request_context: APIRequestContext) -> None:
    new_todo = {
        "title": "Playwright E2E 테스트 작성",
        "completed": False,
        "userId": 1,
    }
    response = api_request_context.post("/todos", data=new_todo)

    assert response.status == 201
    created = response.json()
    assert created["title"] == new_todo["title"]
    assert "id" in created
```

---

## 테스트 실행

```bash
# API 테스트 실행 (브라우저 불필요)
uv run pytest tests/06_api/ -v

# 마커로 실행
uv run pytest -m api -v
```

---

| 이전 | 다음 |
|------|------|
| [← 06. 대기 전략 & 네트워크](./06-waiting-and-network.md) | [08. pytest 통합 →](./08-pytest-integration.md) |
