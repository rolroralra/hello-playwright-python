# 01. Playwright 소개 및 환경 설정

## Playwright란?

Playwright는 Microsoft가 만든 오픈소스 E2E(End-to-End) 테스트 프레임워크입니다.
하나의 API로 **Chromium, Firefox, WebKit** 세 브라우저를 모두 자동화할 수 있습니다.

### 서버 개발자에게 Playwright가 필요한 이유

서버 개발자는 주로 유닛 테스트와 통합 테스트에 집중하지만, 실제 사용자 경험은 **브라우저에서 발생**합니다.

```
유닛 테스트  →  통합 테스트  →  E2E 테스트
(빠름, 격리됨)               (느림, 실제 환경)
```

Playwright로 E2E 테스트를 작성하면:
- API 응답이 UI에 정상적으로 반영되는지 검증
- 인증 플로우(로그인 → 토큰 발급 → 인가) 시나리오 테스트
- 배포 전 핵심 사용자 경로(Critical Path) 자동 검증
- 회귀 테스트 자동화로 배포 자신감 향상

---

## 설치

### 1. uv 설치

`uv`는 Rust로 작성된 초고속 Python 패키지 매니저입니다.
`pip + venv` 조합을 하나의 도구로 대체하며, pip보다 **10~100배 빠릅니다**.

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. 의존성 설치

`uv sync` 하나로 가상환경 생성과 패키지 설치를 동시에 처리합니다.

```bash
uv sync
```

> 📄 참고: [`pyproject.toml`](../pyproject.toml) — 의존성과 pytest 설정이 함께 있습니다.

내부적으로 일어나는 일:
1. `.venv/` 가상환경 자동 생성
2. `pyproject.toml`의 의존성 설치
3. `uv.lock` 파일 생성 (재현 가능한 빌드 보장)

### 3. 브라우저 바이너리 설치

Playwright는 자체 브라우저 바이너리를 별도로 설치합니다.

```bash
# 특정 브라우저만 설치
uv run playwright install chromium

# 세 브라우저 모두 설치
uv run playwright install
```

### 4. 설치 확인

```bash
uv run playwright --version
# Playwright 1.50.0
```

> **`uv run` vs 가상환경 활성화**
> `uv run <명령어>` 는 가상환경을 활성화하지 않고도 프로젝트 환경에서 명령어를 실행합니다.
> `source .venv/bin/activate`를 매번 실행할 필요가 없습니다.

---

## 프로젝트 구조

이 교육 프로젝트의 전체 구조입니다.

```
hello-playwright-python/
├── pyproject.toml            # 의존성 + pytest 설정 (uv)
├── uv.lock                   # 재현 가능한 빌드를 위한 lock 파일
├── conftest.py               # 공통 픽스처
│
├── docs/                     # 교육 문서
│   ├── 01-introduction.md    ← 현재 문서
│   ├── 02-first-test.md
│   ├── 03-selectors.md
│   ├── 04-actions.md
│   ├── 05-assertions.md
│   ├── 06-waiting-and-network.md
│   ├── 07-api-testing.md
│   ├── 08-pytest-integration.md
│   ├── 09-page-object-model.md
│   └── 10-e2e-strategy.md
│
├── tests/                    # 실습 코드
│   ├── 01_basic/
│   ├── 02_selectors/
│   ├── 03_actions/
│   ├── 04_assertions/
│   ├── 05_waiting/
│   ├── 06_api/
│   ├── 07_pom/
│   └── 08_e2e/
│
└── pages/                    # Page Object Model
    ├── base_page.py
    ├── todo_page.py
    └── ...
```

---

## Playwright의 핵심 개념

### Browser / BrowserContext / Page 계층 구조

```
Browser
  └── BrowserContext (독립된 세션, 쿠키 격리)
        └── Page (실제 탭)
```

| 객체 | 역할 | 비유 |
|------|------|------|
| `Browser` | 브라우저 프로세스 | Chrome 앱 |
| `BrowserContext` | 독립 세션(쿠키/스토리지 격리) | 시크릿 창 |
| `Page` | 실제 탭 | 탭 하나 |

### 동기 vs 비동기 API

Playwright는 Python에서 두 가지 방식을 지원합니다.

```python
# 동기 방식 (pytest와 함께 주로 사용)
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://example.com")
    browser.close()
```

```python
# 비동기 방식 (async/await)
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://example.com")
        await browser.close()

asyncio.run(main())
```

> **이 교육 과정은 `pytest-playwright`를 사용하는 동기 방식을 기준으로 합니다.**

---

## 첫 번째 실행

설치가 완료되면 바로 테스트를 실행해 봅시다.

```bash
# 전체 테스트 실행
uv run pytest

# 특정 디렉토리만 실행
uv run pytest tests/01_basic/

# 헤드리스 OFF (브라우저 화면 보기)
uv run pytest --headed

# 느리게 실행 (디버깅용, ms 단위)
uv run pytest --headed --slowmo 1000

# 특정 브라우저 지정
uv run pytest --browser firefox
```

---

## 다음 챕터 예고

다음 챕터에서는 실제로 첫 번째 테스트를 작성하고 실행해봅니다.

---

| 이전 | 다음 |
|------|------|
| - | [02. 첫 번째 테스트 작성 →](./02-first-test.md) |
