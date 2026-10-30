from playwright.sync_api import Page, expect


def test_ferries_booking(auth_page: Page):
    auth_page.goto("https://phptravels.net")
    auth_page.get_by_role("tab", name="Ferries").click()
    auth_page.locator("input[placeholder='Departure Port']").fill("Tarifa")
    auth_page.wait_for_timeout(1000)
    auth_page.get_by_text("Tarifa", exact=True).first.click()
    auth_page.locator("input[placeholder='Arrival Port']").fill("Tangier")
    auth_page.wait_for_timeout(1000)
    auth_page.get_by_text("Tangier", exact=True).first.click()
    auth_page.get_by_role("button", name="Search").click()
    auth_page.wait_for_timeout(2000)
    expect(auth_page.get_by_text("sailings", exact=False)).to_be_visible(timeout=15000)
    auth_page.get_by_role("button", name="Book Now").first.click()
    auth_page.wait_for_timeout(2000)
    auth_page.wait_for_url("**/booking/**", timeout=10000)
    auth_page.locator("label[for='payment_5']").click()
    auth_page.locator("#terms_accepted").check(force=True)
    auth_page.get_by_role("button", name="Confirm Booking").click()
    auth_page.wait_for_url("**/invoice/**", timeout=15000)
    expect(auth_page.get_by_text("Invoice", exact=False).first).to_be_visible()

    print("[SUCCESS] Ferries booked!")



