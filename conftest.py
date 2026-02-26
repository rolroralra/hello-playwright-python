"""
pytest-playwright 전역 픽스처 및 설정

pytest-playwright 플러그인이 browser, page, context 픽스처를 자동 제공합니다.
이 파일에는 프로젝트 전반에서 공유하는 커스텀 픽스처를 정의합니다.
"""
import sys
import os

# pages/ 디렉토리를 import 경로에 추가
sys.path.insert(0, os.path.dirname(__file__))

import pytest
from playwright.sync_api import Page, BrowserContext


# ── 기본 URL 설정 ────────────────────────────────────────────────────────────
BASE_URL = "https://demo.playwright.dev/todomvc"
API_BASE_URL = "https://jsonplaceholder.typicode.com"


@pytest.fixture(scope="session")
def base_url() -> str:
    """테스트 전체에서 공통으로 사용하는 기본 URL."""
    return BASE_URL


@pytest.fixture(scope="session")
def api_base_url() -> str:
    """API 테스트에서 공통으로 사용하는 기본 URL."""
    return API_BASE_URL


# ── 공통 컨텍스트 픽스처 ──────────────────────────────────────────────────────
@pytest.fixture
def todo_page(page: Page, base_url: str) -> Page:
    """TodoMVC 앱으로 이동한 page 픽스처."""
    page.goto(base_url)
    return page
