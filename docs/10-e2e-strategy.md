# 10. E2E 테스트 전략

## 서버 개발자를 위한 E2E 테스트 전략

이 챕터는 지금까지 배운 모든 내용을 종합해서
**실제 웹 서비스에 E2E 테스트를 적용하는 전략**을 다룹니다.

---

## 테스트 피라미드

```
         /\
        /E2E\         적음 (느림, 비용 높음)
       /------\
      /통합 테스트\    중간
     /------------\
    /   유닛 테스트  \ 많음 (빠름, 비용 낮음)
   /________________\
```

E2E 테스트는 **최상위 계층**으로, 전체 시스템이 통합된 상태에서의 동작을 검증합니다.
수가 적어야 하지만, 핵심 사용자 경로는 반드시 포함해야 합니다.

---

## 무엇을 E2E로 테스트해야 하나?

### ✅ E2E 테스트에 적합한 것

1. **Critical Path (핵심 경로)**
   - 회원가입 → 로그인 → 주요 기능 사용 → 로그아웃
   - 상품 조회 → 장바구니 → 결제 → 주문 확인
   - 데이터 생성 → 조회 → 수정 → 삭제 (CRUD 흐름)

2. **인증/인가 흐름**
   - 로그인하지 않은 사용자가 보호된 페이지에 접근 시 리다이렉트
   - 권한 없는 사용자의 관리자 기능 차단

3. **API와 UI의 통합 지점**
   - API가 반환한 데이터가 UI에 올바르게 표시되는지
   - UI 액션이 API를 올바르게 호출하는지

### ❌ E2E로 하지 말아야 하는 것

- 단순 계산 로직 (유닛 테스트로)
- 개별 API 엔드포인트 테스트 (통합 테스트로)
- UI 스타일, 디자인 검증 (시각적 회귀 테스트로)

---

## 테스트 시나리오 설계

### Given-When-Then 패턴

```python
def test_user_can_complete_purchase(
    self,
    page: Page,
    api: APIRequestContext,
) -> None:
    """
    시나리오: 사용자가 상품을 구매한다

    Given: 로그인된 사용자, 재고 있는 상품
    When: 상품 선택 → 장바구니 → 결제
    Then: 주문 완료 페이지 표시, 주문 DB에 저장
    """
    # Given: API로 테스트 데이터 준비
    product = api.post("/products", data={"name": "테스트 상품", "stock": 10}).json()

    # When: UI 흐름
    page.goto(f"/products/{product['id']}")
    page.get_by_role("button", name="장바구니 담기").click()
    page.get_by_role("link", name="장바구니").click()
    page.get_by_role("button", name="결제하기").click()
    page.get_by_label("카드번호").fill("4111111111111111")
    page.get_by_role("button", name="결제 완료").click()

    # Then: UI 검증
    expect(page.get_by_role("heading", name="주문 완료")).to_be_visible()
    order_id = page.get_by_test_id("order-id").inner_text()

    # Then: API로 백엔드 상태 검증
    order = api.get(f"/orders/{order_id}").json()
    assert order["status"] == "CONFIRMED"
    assert order["product_id"] == product["id"]
```

---

## 테스트 데이터 전략

### 전략 1: API로 데이터 생성 (권장)

```python
@pytest.fixture
def test_product(api: APIRequestContext) -> dict:
    """각 테스트마다 새 상품 생성."""
    product = api.post(
        "/products",
        data={"name": f"테스트상품_{uuid4()}", "price": 1000},
    ).json()
    yield product
    # 테스트 후 정리
    api.delete(f"/products/{product['id']}")
```

### 전략 2: 고정 테스트 데이터 사용

```python
# 항상 존재하는 시드 데이터 사용 (개발/스테이징 환경에서)
TEST_PRODUCT_ID = "fixture-product-001"

def test_product_detail(page: Page) -> None:
    page.goto(f"/products/{TEST_PRODUCT_ID}")
    expect(page.get_by_role("heading")).to_contain_text("테스트 상품")
```

---

## 환경 설정 분리

```python
# conftest.py
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080")
TEST_USER_EMAIL = os.getenv("TEST_USER_EMAIL", "test@example.com")
TEST_USER_PASSWORD = os.getenv("TEST_USER_PASSWORD", "testpass123")


@pytest.fixture(scope="session")
def api(playwright: Playwright) -> APIRequestContext:
    return playwright.request.new_context(base_url=API_BASE_URL)
```

```bash
# 로컬 개발
BASE_URL=http://localhost:3000 pytest -m e2e

# 스테이징 환경
BASE_URL=https://staging.myapp.com pytest -m e2e

# 프로덕션 (smoke test만)
BASE_URL=https://myapp.com pytest -m smoke
```

---

## 로그인 상태 관리 — Storage State

매번 로그인하는 것은 느립니다. Storage State를 사용해 인증 상태를 재사용합니다.

```python
# 1. 한 번만 로그인하고 상태 저장
@pytest.fixture(scope="session")
def auth_state(playwright: Playwright) -> str:
    """세션당 한 번만 로그인하고 상태를 저장합니다."""
    browser = playwright.chromium.launch()
    context = browser.new_context()
    page = context.new_page()

    page.goto(f"{BASE_URL}/login")
    page.get_by_label("이메일").fill(TEST_USER_EMAIL)
    page.get_by_label("비밀번호").fill(TEST_USER_PASSWORD)
    page.get_by_role("button", name="로그인").click()
    page.wait_for_url(f"{BASE_URL}/dashboard")

    state_path = "/tmp/auth_state.json"
    context.storage_state(path=state_path)
    browser.close()
    return state_path


# 2. 저장된 상태로 브라우저 컨텍스트 생성
@pytest.fixture
def logged_in_page(browser, auth_state: str) -> Page:
    context = browser.new_context(storage_state=auth_state)
    page = context.new_page()
    yield page
    context.close()
```

---

## CI/CD 통합

### GitHub Actions 예시

```yaml
# .github/workflows/e2e.yml
name: E2E Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install --with-deps chromium

      - name: Start app (if needed)
        run: docker-compose up -d

      - name: Run E2E tests
        env:
          BASE_URL: http://localhost:3000
        run: |
          pytest -m "smoke or e2e" \
            --browser chromium \
            --screenshot=only-on-failure \
            --video=retain-on-failure \
            --output=test-results \
            --html=reports/report.html \
            --self-contained-html

      - name: Upload test artifacts
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: |
            test-results/
            reports/
```

---

## 테스트 안정성 향상

### Flaky Test 방지

```python
# ❌ 이렇게 하면 안 됨
import time
time.sleep(3)
assert page.get_by_role("button").is_visible()

# ✅ 이렇게 해야 함
expect(page.get_by_role("button")).to_be_visible(timeout=10_000)
```

### 재시도 설정

```ini
# pytest.ini
[pytest]
# 실패한 테스트 2번 재시도
# pip install pytest-rerunfailures 필요
addopts = --reruns 2 --reruns-delay 1
```

### 테스트 격리

```python
# ❌ 테스트 간 상태 공유 (나쁜 예)
class TestOrder:
    order_id = None

    def test_create_order(self):
        TestOrder.order_id = ...  # 다음 테스트에 영향

# ✅ 픽스처로 독립적 데이터 (좋은 예)
@pytest.fixture
def new_order(api):
    order = api.post("/orders", data={...}).json()
    yield order
    api.delete(f"/orders/{order['id']}")
```

---

## 실습 코드

> 📄 [`tests/08_e2e/test_e2e_scenario.py`](../tests/08_e2e/test_e2e_scenario.py)

### 핵심 경로 테스트 (Critical Path)

```python
@pytest.mark.smoke
@pytest.mark.e2e
class TestCriticalPath:
    def test_create_todo_end_to_end(self, todo_page: TodoPage) -> None:
        # Given
        todo_page.should_have_count(0)

        # When
        todo_page.add_todo("E2E 테스트 작성하기")

        # Then
        todo_page.should_have_count(1)
        todo_page.should_contain_todo("E2E 테스트 작성하기")
```

---

## E2E 테스트 실행

```bash
# 전체 E2E 테스트
pytest tests/08_e2e/ -v --headed

# smoke 테스트만 (빠른 검증)
pytest -m smoke -v

# 비디오 녹화와 함께
pytest tests/08_e2e/ -v --video=on --output=test-results

# 실패 시 스크린샷
pytest tests/08_e2e/ -v --screenshot=only-on-failure
```

---

## 여기서 끝이 아닙니다

이 교육 과정을 마친 후 실제 프로젝트에 적용할 때 참고할 자료:

- [Playwright Python 공식 문서](https://playwright.dev/python/docs/intro)
- [pytest-playwright 문서](https://playwright.dev/python/docs/test-runners)
- [Best Practices](https://playwright.dev/python/docs/best-practices)
- [Trace Viewer](https://playwright.dev/python/docs/trace-viewer)

---

| 이전 | 다음 |
|------|------|
| [← 09. Page Object Model](./09-page-object-model.md) | - |
