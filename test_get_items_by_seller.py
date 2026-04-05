from conftest import assert_item_schema, assert_json_content_type, build_item_payload, extract_created_id, extract_items, get_items_by_seller


def test_case_21_get_items_by_seller_with_multiple_items(session, base_url, create_item, seller_id):
    response_1 = create_item(build_item_payload(seller_id, "Seller item 1", 100, 1, 10, 1))
    response_2 = create_item(build_item_payload(seller_id, "Seller item 2", 200, 2, 20, 2))

    assert response_1.status_code == 200
    assert response_2.status_code == 200

    id_1 = extract_created_id(response_1)
    id_2 = extract_created_id(response_2)

    response = get_items_by_seller(session, base_url, seller_id)

    assert response.status_code == 200
    assert_json_content_type(response)

    items = extract_items(response)
    ids = [item["id"] for item in items]
    assert id_1 in ids
    assert id_2 in ids

    for item in items:
        assert item["sellerId"] == seller_id
        assert_item_schema(item)



def test_case_22_get_items_by_seller_with_no_items(session, base_url, unused_seller_id):
    response = get_items_by_seller(session, base_url, unused_seller_id)

    assert response.status_code == 200
    assert_json_content_type(response)
    assert response.json() == []



def test_case_23_get_items_by_nonexistent_seller(session, base_url):
    response = get_items_by_seller(session, base_url, 999999999)

    assert response.status_code == 200
    assert_json_content_type(response)
    assert response.json() == []



def test_case_24_get_items_by_malformed_seller_id(session, base_url):
    response = session.get(f"{base_url}/api/1/abc/item")

    assert response.status_code == 400
    assert_json_content_type(response)



def test_case_25_get_items_by_seller_is_idempotent(session, base_url, create_item, seller_id):
    payload = build_item_payload(seller_id, "Idempotent seller item", 999, 3, 30, 1)
    created = create_item(payload)
    assert created.status_code == 200

    first_response = get_items_by_seller(session, base_url, seller_id)
    second_response = get_items_by_seller(session, base_url, seller_id)

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.json() == second_response.json()
