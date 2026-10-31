import os
from playwright.sync_api import Page, expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://phptravels.net")
EMAIL = os.getenv("CUSTOMER_EMAIL", "user@phptravels.com")
PASSWORD = os.getenv("CUSTOMER_PASSWORD", "demouser")


def handle_popups(page: Page):
    """Pop-up warning about the website being demo"""
    demo_modal = page.locator("#demoWarningModal")

    try:
        expect(demo_modal).to_be_visible(timeout=15000)
        print("[DEBUG] Demo warning modal appeared.")

        btn = demo_modal.get_by_role("button", name="I Understand & Continue")
        expect(btn).to_be_visible(timeout=5000)
        expect(btn).to_be_enabled(timeout=5000)

        btn.click()

        expect(demo_modal).to_be_hidden(timeout=15000)
        print("[DEBUG] Demo warning modal closed successfully.")
    except PlaywrightTimeoutError:
        print("[DEBUG] Modal didn't appear or didn't close. Proceeding...")
        pass


def test_successful_login(page: Page):
    page.goto(f"{BASE_URL}/login", wait_until="networkidle")

    handle_popups(page)

    page.locator("#email").fill(EMAIL)
    page.locator("#password").fill(PASSWORD)

    login_btn = page.locator("button", has_text="Sign In to your account")
    expect(login_btn).to_be_visible(timeout=10000)
    login_btn.click()

    page.wait_for_url("**/dashboard", timeout=20000)
    assert "dashboard" in page.url
    print("\n[SUCCESS] I'm in! Login successful.")


def test_failed_login(page: Page):
    page.goto(f"{BASE_URL}/login", wait_until="networkidle")

    handle_popups(page)

    page.locator("#email").fill("user@phptravelscom")
    page.locator("#password").fill(PASSWORD)

    login_btn = page.locator("button", has_text="Sign In to your account")
    expect(login_btn).to_be_visible(timeout=10000)
    login_btn.click()

    expect(page.get_by_text("Invalid Credentials", exact=False)).to_be_visible(timeout=15000)
    print("\n[SUCCESS] Negative test passed! I'm not in (as expected).")