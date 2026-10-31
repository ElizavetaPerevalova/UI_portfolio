import time
from playwright.sync_api import Playwright


def test_ferries_search(playwright: Playwright):
    """
    Test the POST /api/ferries/search endpoint.
    Verify that the API returns a 200 OK status, success flag, and a non-empty list of ferries.
    """
    request = playwright.request.new_context(base_url="https://phptravels.net")
    payload = {
        "departure_port_id": 17,
        "destination_port_id": 10,
        "date": "2026-10-31",
        "trip_type": "oneway",
        "return_date": None,
        "adults": 1,
        "children": 0,
        "infant": 0,
        "passengers": [
            {
                "id": 1,
                "ticket_type_id": 10,
                "passenger_category": "adult"
            }
        ],
        "vehicles": [],
        "pets": [],
        "bonuses": [],
        "vehicle_type_hint": "",
        "pet_type_hint": "",
        "supplier": "kikoto"
    }

    start_time = time.time()
    response = request.post("/api/ferries/search", data=payload)
    end_time = time.time()
    response_time = end_time - start_time

    print(f"\n[INFO] HTTP Status: {response.status}")
    print(f"[INFO] Server response time: {response_time:.2f} seconds")
    assert response.status == 200, f"Expected 200, got {response.status}"

    data = response.json()
    assert data["success"] is True, "API returned success: False"
    assert data["message"] == "OK", f"API message: {data['message']}"

    outbound_ferries = data["data"]["outbound"]
    assert len(outbound_ferries) > 0, "No ferries found for the given dates!"

    first_ferry = outbound_ferries[0]
    ship_name = first_ferry["ship_name"]
    company = first_ferry["shipping_company"]["name"]
    departure_time = first_ferry["departure_datetime"]

    print(f"[INFO] Found ferries: {len(outbound_ferries)}")
    print(f"[INFO] First ferry: {ship_name} ({company})")
    print(f"[INFO] Departure: {departure_time}")

    print("[SUCCESS] API test passed! Ferries found.")