from playwright.sync_api import Page, expect


def test_successful_login(page: Page):
    page.goto("https://phptravels.net/login")
    page.get_by_role("button", name="I Understand & Continue").click()

    page.locator("#email").fill("user@phptravels.com")
    page.locator("#password").fill("demouser")

    page.get_by_role("button", name="login Sign In to your account").click()

    page.wait_for_url("**/dashboard")
    assert "dashboard" in page.url
    print("\nI'm in")

def test_failed_login(page: Page):
    page.goto("https://phptravels.net/login")
    page.get_by_role("button", name="I Understand & Continue").click()

    page.locator("#email").fill("user@phptravelscom")
    page.locator("#password").fill("demouser")

    page.get_by_role("button", name="login Sign In to your account").click()
    expect(page.get_by_text("Error Invalid Credentials")).to_be_visible()

    print("\nI'm not in(((")