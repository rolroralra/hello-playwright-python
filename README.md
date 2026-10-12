# Playwright Python 교육 — 서버 개발자를 위한 E2E 테스트

Python으로 Playwright를 배우고, 담당 웹 서비스에 E2E 테스트를 적용합니다.

## 목표

이 교육 과정을 마치면:
- Playwright Python API를 자신 있게 사용할 수 있습니다
- 서버 API와 UI를 결합한 E2E 테스트를 작성할 수 있습니다
- CI/CD 파이프라인에 E2E 테스트를 통합할 수 있습니다

---

## 빠른 시작

```bash
# 1. uv 설치 (없는 경우)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 의존성 설치 (venv 생성 + 패키지 설치를 한 번에)
uv sync

# 3. 브라우저 설치
uv run playwright install chromium

# 4. 테스트 실행
uv run pytest tests/01_basic/ -v --headed
```

---

## 교육 목차

| # | 챕터 | 핵심 내용 | 실습 코드 |
|---|------|-----------|-----------|
| 01 | [소개 및 환경 설정](docs/01-introduction.md) | 설치, 프로젝트 구조, 기본 개념 | `tests/01_basic/` |
| 02 | [첫 번째 테스트](docs/02-first-test.md) | pytest-playwright 픽스처, 테스트 실행 | `tests/01_basic/` |
| 03 | [셀렉터](docs/03-selectors.md) | role, text, CSS, XPath, 체이닝 | `tests/02_selectors/` |
| 04 | [사용자 액션](docs/04-actions.md) | 클릭, 입력, 키보드, 폼 조작 | `tests/03_actions/` |
| 05 | [단언 (Assertions)](docs/05-assertions.md) | expect API, Auto-retrying | `tests/04_assertions/` |
| 06 | [대기 전략 & 네트워크](docs/06-waiting-and-network.md) | Auto-waiting, route, 모킹 | `tests/05_waiting/` |
| 07 | [API 테스팅](docs/07-api-testing.md) | APIRequestContext, CRUD, UI+API 결합 | `tests/06_api/` |
| 08 | [pytest 통합](docs/08-pytest-integration.md) | 픽스처, 마커, 파라미터화, CI 옵션 | `tests/07_pom/` |
| 09 | [Page Object Model](docs/09-page-object-model.md) | POM 패턴, BasePage, 메서드 체이닝 | `tests/07_pom/` |
| 10 | [E2E 테스트 전략](docs/10-e2e-strategy.md) | Critical Path, CI/CD, Storage State | `tests/08_e2e/` |

---

## 프로젝트 구조

```
hello-playwright-python/
├── pyproject.toml          # 의존성 + pytest 설정 (uv)
├── uv.lock                 # 재현 가능한 빌드를 위한 lock 파일
├── conftest.py             # 공통 픽스처
│
├── docs/                   # 교육 문서 (챕터별)
│
├── pages/                  # Page Object Model
│   ├── base_page.py
│   └── todo_page.py
│
└── tests/
    ├── 01_basic/           # 챕터 01-02: 첫 테스트
    ├── 02_selectors/       # 챕터 03: 셀렉터
    ├── 03_actions/         # 챕터 04: 액션
    ├── 04_assertions/      # 챕터 05: 단언
    ├── 05_waiting/         # 챕터 06: 대기 & 네트워크
    ├── 06_api/             # 챕터 07: API 테스팅
    ├── 07_pom/             # 챕터 08-09: POM
    └── 08_e2e/             # 챕터 10: E2E 전략
```

---

## 자주 쓰는 명령어

```bash
# 챕터별 실행
uv run pytest tests/01_basic/ -v --headed

# 마커로 실행
uv run pytest -m smoke -v
uv run pytest -m e2e -v
uv run pytest -m api -v

# 브라우저 선택
uv run pytest --browser firefox
uv run pytest --browser webkit

# 디버그 모드 (Inspector GUI)
PWDEBUG=1 uv run pytest tests/08_e2e/ --headed

# 코드 생성기 (브라우저 조작을 pytest 코드로 기록)
uv run playwright codegen --target python-pytest https://demo.playwright.dev/todomvc

# 비디오 + 스크린샷 (CI용)
uv run pytest -m e2e --video=retain-on-failure --screenshot=only-on-failure --output=test-results

# HTML 리포트
uv run pytest --html=reports/report.html --self-contained-html
```

---

## 실습 앱

| 앱 | URL | 용도 |
|----|-----|------|
| TodoMVC | https://demo.playwright.dev/todomvc | UI 테스트 실습 |
| Playwright 홈 | https://playwright.dev | 기본 탐색 실습 |
| JSONPlaceholder | https://jsonplaceholder.typicode.com | API 테스트 실습 |
