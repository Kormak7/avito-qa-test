from conftest import assert_item_schema, assert_json_content_type, extract_items, find_item, get_item_by_id


def test_case_17_get_item_by_existing_id(session, base_url, create_valid_item):
    created = create_valid_item(name="Existing item", price=65000, likes=10, view_count=150, contacts=3)
    response = get_item_by_id(session, base_url, created["id"])

    assert response.status_code == 200
    assert_json_content_type(response)

    items = extract_items(response)
    item = find_item(items, created["id"])
    assert_item_schema(item)
    assert item["sellerId"] == created["sellerId"]
    assert item["name"] == created["name"]
    assert item["price"] == created["price"]
    assert item["statistics"] == created["statistics"]



def test_case_18_get_item_by_nonexistent_id(session, base_url):
    response = get_item_by_id(session, base_url, "11111111-1111-1111-1111-111111111111")

    assert response.status_code == 404
    assert_json_content_type(response)



def test_case_19_get_item_by_malformed_id(session, base_url):
    response = get_item_by_id(session, base_url, "invalid id with spaces")

    assert response.status_code == 400
    assert_json_content_type(response)



def test_case_20_get_item_is_idempotent(session, base_url, create_valid_item):
    created = create_valid_item(name="Idempotency item", price=101, likes=1, view_count=2, contacts=3)

    first_response = get_item_by_id(session, base_url, created["id"])
    second_response = get_item_by_id(session, base_url, created["id"])

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.json() == second_response.json()
