from playwright.sync_api import sync_playwright
import sys
import os
import pytest


# logging
class Tee:
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for f in self.files:
            if not getattr(f, 'closed', False):
                try:
                    f.write(obj)
                    f.flush()
                except ValueError:
                    pass

    def flush(self):
        for f in self.files:
            if not getattr(f, 'closed', False):
                try:
                    f.flush()
                except ValueError:
                    pass

    def __getattr__(self, name):
        return getattr(self.files[0], name)


_log_file = None


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    global _log_file
    log_path = os.path.join(config.rootpath, "last_test_run.log")
    _log_file = open(log_path, "w", encoding="utf-8")
    sys.stdout = Tee(sys.stdout, _log_file)
    sys.stderr = Tee(sys.stderr, _log_file)


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    global _log_file
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__


def _close_demo_modal(page):
    try:
        modal = page.locator("#demoWarningModal")
        if modal.is_visible(timeout=3000):
            modal.get_by_role("button").first.click()
            page.wait_for_timeout(500)
    except Exception:
        pass


@pytest.fixture(scope="session", autouse=True)
def logged_in_session():
    auth_file = "auth.json"

    if os.path.exists(auth_file):
        print(f"[conftest] deleted previous {auth_file}")
        os.remove(auth_file)

    print("[conftest] login again")
    with sync_playwright() as p:
        # ИЗМЕНЕНИЕ 1: Добавили args=["--start-maximized"]
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])

        # ИЗМЕНЕНИЕ 2: Добавили no_viewport=True
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        try:
            page.goto("https://phptravels.net", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle", timeout=15000)
            _close_demo_modal(page)

            try:
                cookie = page.get_by_role("button", name="I Understand & Continue")
                cookie.wait_for(state="visible", timeout=8000)
                cookie.click()
                page.wait_for_timeout(500)
            except Exception:
                pass

            _close_demo_modal(page)

            login_link = page.get_by_role("link", name="Login").first
            login_link.wait_for(state="visible", timeout=10000)
            login_link.click()
            page.wait_for_url("**/login", timeout=15000)
            print("[conftest] on the login page")

            page.locator("#email").fill("user@phptravels.com")
            page.locator("#password").fill("demouser")
            page.locator("#password").press("Enter")

            page.wait_for_url("**/dashboard", timeout=20000)
            print("[conftest] successful login")

            context.storage_state(path=auth_file)
            print(f"[conftest] {auth_file} saved")

        finally:
            browser.close()


@pytest.fixture
def auth_page():
    with sync_playwright() as p:
        # ИЗМЕНЕНИЕ 3: Добавили args=["--start-maximized"]
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])

        # ИЗМЕНЕНИЕ 4: Добавили no_viewport=True
        context = browser.new_context(
            storage_state="auth.json",
            no_viewport=True
        )
        page = context.new_page()
        yield page
        browser.close()