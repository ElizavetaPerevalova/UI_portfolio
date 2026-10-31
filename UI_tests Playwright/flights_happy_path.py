import re
from datetime import datetime
from playwright.sync_api import Page


def test_flight_booking(logged_in_session, auth_page: Page):
    auth_page.goto("https://phptravels.net", wait_until="domcontentloaded")
    print("[START] URL after 1st goto:", auth_page.url)

    if "/flights/" in auth_page.url:
        print("[FIX] redirect to results — clear localStorage and cookies")
        auth_page.evaluate("localStorage.clear()")
        auth_page.context.clear_cookies()
        auth_page.goto("https://phptravels.net", wait_until="domcontentloaded")
        print("[FIX] URL after clear:", auth_page.url)

    # 2. DEMO-MODAL click
    demo_modal = auth_page.locator("#demoWarningModal")
    if demo_modal.is_visible(timeout=3000):
        print("[FIX] Demo-modal is visible")
        demo_modal.get_by_role("button").first.click()
        print("[FIX] Demo-modal is closed")
    else:
        print("[FIX] No Demo-modal")

    # flights page
    auth_page.get_by_role("button", name="Flights").click()

    # Wait for the From field to appear
    auth_page.locator("#fl_from_trigger").wait_for(state="visible", timeout=15000)
    print("[STEP] Flights page is opened:", auth_page.url)

    # Close cookie banner if it exists
    try:
        cookie = auth_page.get_by_role("button", name="I Understand & Continue")
        cookie.wait_for(state="visible", timeout=3000)
        cookie.click()
    except Exception:
        print("[FIX] No Cookie window")

    # from ...to...
    auth_page.locator("#fl_from_trigger").click()
    auth_page.locator("#fl_from_q").fill("New York")

    all_airports = auth_page.locator("#fl_from_panel").get_by_text("All Airports").first
    all_airports.wait_for(state="visible", timeout=15000)
    all_airports.click()
    print("[STEP] FROM chosen: New York")

    auth_page.locator("#fl_to_trigger").click()
    auth_page.locator("#fl_to_q").fill("Los Angeles")

    lax = auth_page.locator("#fl_to_panel").get_by_text("Los Angeles International Airport").first
    lax.wait_for(state="visible", timeout=15000)
    lax.click()
    print("[STEP] TO chosen: Los Angeles")

    # choose today in the date block
    auth_page.locator("#flights_departure_date").click()
    picker = auth_page.locator(".datepicker").first
    picker.wait_for(state="attached")
    today_day = str(datetime.now().day)

    auth_page.evaluate("""(day) => {
        const divs = document.querySelectorAll('.datepicker .day:not(.old):not(.new)');
        for (const div of divs) {
            if (div.textContent.trim() === day) {
                div.click();
                break;
            }
        }
    }""", today_day)
    print(f"[STEP] Date is chosen: {today_day}")

    print("\n[BEFORE SEARCH] URL:", auth_page.url)
    print("[BEFORE SEARCH] From:", auth_page.locator("#fl_from_trigger").inner_text())
    print("[BEFORE SEARCH] to:", auth_page.locator("#fl_to_trigger").inner_text())

    auth_page.locator(
        "form:has(#fl_from_trigger) button[type='submit'].search-btn"
    ).click()

    auth_page.wait_for_url("**/flights/**", timeout=30000)
    print("\n[AFTER SEARCH] URL:", auth_page.url)

    # waiting for the results
    results_marker = auth_page.get_by_text(
        re.compile(r"Found from \d+ Supplier\(s\)")
    )
    results_marker.wait_for(state="visible", timeout=60000)
    print("[INFO] Results are ready:", results_marker.inner_text())

    # waiting for ticket cards to be visible
    book_btn = auth_page.locator("[data-rbac-book]:visible").first
    book_btn.wait_for(state="visible", timeout=60000)
    print("[INFO] Tickets are ready")

    # number of found flights
    flights_count = auth_page.get_by_text(
        re.compile(r"\d+\s+Flight(s)?")
    ).first
    if flights_count.is_visible(timeout=3000):
        print("[INFO] Tickets found:", flights_count.inner_text())

    # booking
    book_btn.scroll_into_view_if_needed()
    book_btn.click()
    print("[INFO] click on Book Now")

    # waiting for booking redirect
    auth_page.wait_for_url("**/flights/booking/**", timeout=30000)
    print("[INFO] redirect to booking:", auth_page.url)

    print("\n[SUCCESS] search -> results -> booking")
    print("=" * 60 + "\n")

    # waiting for loader
    loader = auth_page.get_by_text("Preparing your booking")
    try:
        loader.wait_for(state="visible", timeout=10000)
    except Exception:
        pass
    try:
        loader.wait_for(state="hidden", timeout=30000)
    except Exception:
        pass

    # Flight package page -> Baggage
    next_btn = auth_page.get_by_role("button", name="Next")
    next_btn.wait_for(state="visible", timeout=30000)
    next_btn.click()
    auth_page.wait_for_url("**#baggage", timeout=10000)
    print("[INFO] Flight package is visible, we go to Baggage")

    # Baggage page -> Seats
    next_btn = auth_page.get_by_role("button", name="Next")
    next_btn.wait_for(state="visible", timeout=30000)
    next_btn.click()
    auth_page.wait_for_url("**#seats", timeout=10000)
    print("[INFO] Baggage page is visible, we go to Seats")

    # Seats page -> Meals
    next_btn = auth_page.get_by_role("button", name="Next")
    next_btn.wait_for(state="visible", timeout=30000)
    next_btn.click()
    auth_page.wait_for_url("**#meals", timeout=10000)
    print("[INFO] Seats page is visible, we go to Meals")

    # Meals page -> Complete booking
    next_btn = auth_page.get_by_role("button", name="Next")
    next_btn.wait_for(state="visible", timeout=30000)
    next_btn.click()
    auth_page.wait_for_url("**#complete", timeout=10000)
    print("[INFO] Meals page is visible, we go to Complete your booking")

    # forms final
    auth_page.wait_for_url("**#complete", timeout=15000)
    print("\n[FINAL] URL:", auth_page.url)

    # ---------- helper ----------
    def fill_if_needed(selector, value):
        el = auth_page.locator(selector).first
        if el.is_enabled() and not el.input_value():
            el.fill(value)
            print(f"   FILLED {selector} = {value!r}")
            return True
        return False

    # ---------- Guest Details ----------
    print("[FINAL] Guest Details")
    sel_title = auth_page.locator("select[x-model='primary_guest.title']")
    if sel_title.is_enabled():
        sel_title.select_option(label="Mr")
    fill_if_needed("input[x-model='primary_guest.first_name']", "John")
    fill_if_needed("input[x-model='primary_guest.last_name']", "Doe")
    fill_if_needed("input[x-model='primary_guest.email']", "john.doe@example.com")
    fill_if_needed("input[x-model='primary_guest.phone']", "1234567890")

    # Country Code
    country_inp = auth_page.locator("input[placeholder='Select Country']").first
    if country_inp.is_enabled() and not country_inp.input_value():
        country_inp.click()
        country_inp.fill("United States")
        # ONLY keep wait here for Alpine.js to filter the dropdown
        auth_page.wait_for_timeout(500)
        country_inp.press("ArrowDown")
        country_inp.press("Enter")
        print(f"   Country: {country_inp.input_value()!r}")

    # ---------- Passengers (Happy Path: ONLY 1 ADULT) ----------
    PAX = [
        ("adult_0", "Mr", "John", "Doe", "AB1234567"),
    ]
    for key, title, first, last, passport in PAX:
        print(f"[FINAL] Passenger {key}")
        s = auth_page.locator(f"select[x-model='formData.passengers.{key}.title']")
        if s.is_enabled() and not s.input_value():
            s.select_option(label=title)
        fill_if_needed(f"input[x-model='formData.passengers.{key}.first_name']", first)
        fill_if_needed(f"input[x-model='formData.passengers.{key}.last_name']", last)
        fill_if_needed(f"input[x-model='formData.passengers.{key}.passport_number']", passport)

    # ---------- Nationality ----------
    print("[FINAL] Nationality")
    nats = auth_page.locator("input[placeholder='Select Nationality']")
    for i in range(nats.count()):
        n = nats.nth(i)
        if n.is_visible() and n.is_enabled() and not n.input_value():
            n.click()
            n.fill("Russia")
            # ONLY keep wait here for Alpine.js to filter the dropdown
            auth_page.wait_for_timeout(600)

            n.press("ArrowDown")
            n.press("Enter")
            print(f"   #{i}: {n.input_value()!r}")

            # Close dropdown safely
            auth_page.locator("h3:has-text('Guest Details')").first.click(force=True)

    # ============================================================
    # DOB + Expiry (keyboard + enter)
    # ============================================================
    print("[FINAL] DOB / Passport expiry")

    def close_picker():
        """Closing the calendar safely without clicking 'Back'."""
        auth_page.keyboard.press("Escape")
        try:
            auth_page.locator("h3:has-text('Guest Details')").first.click(force=True)
        except Exception:
            pass

    def fill_date_keyboard(span_loc, year, month, day, label=""):
        """Filling date with keyboard and enter."""
        close_picker()

        span_loc.click(force=True)
        # ONLY keep wait for calendar animation to open
        auth_page.wait_for_timeout(500)

        # year enter (delay=50 helps Alpine.js catch keystrokes)
        auth_page.keyboard.type(str(year), delay=50)
        auth_page.keyboard.press("Enter")
        # ONLY keep wait for transition to Month step
        auth_page.wait_for_timeout(500)

        # month enter
        auth_page.keyboard.type(str(month).zfill(2), delay=50)
        auth_page.keyboard.press("Enter")
        # ONLY keep wait for transition to Day step
        auth_page.wait_for_timeout(500)

        # day enter
        auth_page.keyboard.type(str(day).zfill(2), delay=50)
        auth_page.keyboard.press("Enter")
        # ONLY keep wait for finalizing date
        auth_page.wait_for_timeout(300)

        close_picker()
        print(f"   {label}: {year}-{month}-{day} ✓ (Enter)")

    def fill_passenger_dates(key_label, dob, expiry):
        """Finds and opens the card to fill in data."""
        first_name_input = auth_page.locator(f"input[x-model='formData.passengers.{key_label}.first_name']")
        card = first_name_input.locator("xpath=ancestor::div[contains(@class, 'border')][1]")

        show_btn = card.locator("button[aria-label='Show details']")
        if show_btn.count() > 0 and show_btn.is_visible():
            show_btn.click(force=True)
            auth_page.wait_for_timeout(400) # Wait for accordion to expand

        print(f"[FINAL] Passenger {key_label}")
        spans = card.locator("span[role='button']")

        if spans.count() >= 6:
            fill_date_keyboard(spans.nth(0), *dob, label=f"{key_label} DOB")
            fill_date_keyboard(spans.nth(3), *expiry, label=f"{key_label} expiry")

            hide_btn = card.locator("button[aria-label='Hide details']")
            if hide_btn.count() > 0 and hide_btn.is_visible():
                hide_btn.click(force=True)
        else:
            print(f"   [WARN] Found only {spans.count()} date spans in card {key_label}")

    # passengers dates (only adult_0 for Happy Path)
    fill_passenger_dates("adult_0", (1990, 5, 15), (2028, 5, 15))

    # ---------- Payment ----------
    print("[FINAL] Payment")
    checked = auth_page.locator("input[name='payment']:checked")
    if checked.count() == 0:
        auth_page.locator("input[name='payment']").first.check()
    payment_value = auth_page.locator("input[name='payment']:checked").first.get_attribute("value")
    print(f"   payment: {payment_value}")

    # ---------- Terms ----------
    print("[FINAL] Terms")
    terms_input = auth_page.locator("#terms_accepted")
    terms_box = auth_page.locator(".checkbox-container").filter(has=terms_input).locator(".checkbox-custom").first

    if not terms_input.is_checked():
        terms_box.scroll_into_view_if_needed()
        terms_box.click(force=True)

    is_checked = terms_input.is_checked()
    print(f"   terms checked: {is_checked}")
    assert is_checked, "Terms not checked"

    # ---------- Confirm ----------
    confirm_btn = auth_page.get_by_role("button", name="Confirm Booking")
    confirm_btn.wait_for(state="visible", timeout=10000)

    # Polling loop to check if button is enabled (No blind wait)
    for i in range(20):
        if not confirm_btn.is_disabled():
            print(f"[FINAL] Confirm enabled in {i * 0.5:.1f}s")
            break
        auth_page.wait_for_timeout(500)
    else:
        print("[FINAL] ERROR: Confirm disabled. screenshot: final_form_error.png")
        auth_page.screenshot(path="../final_form_error.png")
        raise AssertionError("Confirm Booking disabled")

    confirm_btn.scroll_into_view_if_needed()
    confirm_btn.click(force=True)
    print("[FINAL] Confirm is clicked")

    # Replaced 5s wait with direct URL wait
    print("[FINAL] waiting invoice...")
    auth_page.wait_for_url("**/invoice/flights/**", timeout=30000)
    print(f"[FINAL] invoice URL : {auth_page.url}")

    try:
        auth_page.locator(".animate-spin").wait_for(state="hidden", timeout=15000)
        print("[FINAL] loading spinner done")
    except Exception:
        pass

    # Invoice header
    invoice_header = auth_page.get_by_text(re.compile(r"Invoice #\d+")).first
    invoice_header.wait_for(state="visible", timeout=15000)
    invoice_number = invoice_header.inner_text().strip()
    print(f"[FINAL] cool we have invoice: {invoice_number}")

    # Checking Total Amount is not null
    total_amount_text = auth_page.get_by_text("Total Amount:", exact=False).locator("..").inner_text()
    print(f"[FINAL] Total Amount: {total_amount_text.strip()}")

    # Assertions for Total Amount
    assert "USD" in total_amount_text, "Total Amount doesn't have USD currency"
    assert "0.00" not in total_amount_text, "Total Amount is zero!"

    print("\n" + "=" * 60)
    print("E2E is done, we can fly")
    print("=" * 60 + "\n")