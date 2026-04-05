from conftest import assert_json_content_type, assert_statistics_schema, build_item_payload, extract_created_id, get_item_by_id, get_statistic


def test_case_26_get_statistic_for_existing_id(session, base_url, create_valid_item):
    created = create_valid_item(name="Statistic item", price=55000, likes=7, view_count=88, contacts=4)
    response = get_statistic(session, base_url, created["id"])

    assert response.status_code == 200
    assert_json_content_type(response)

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    for stats in data:
        assert_statistics_schema(stats)
    assert data[0]["likes"] == created["statistics"]["likes"]
    assert data[0]["viewCount"] == created["statistics"]["viewCount"]
    assert data[0]["contacts"] == created["statistics"]["contacts"]



def test_case_27_get_statistic_for_nonexistent_id(session, base_url):
    response = get_statistic(session, base_url, "11111111-1111-1111-1111-111111111111")

    assert response.status_code == 404
    assert_json_content_type(response)



def test_case_28_get_statistic_for_malformed_id(session, base_url):
    response = get_statistic(session, base_url, "bad id with spaces")

    assert response.status_code == 400
    assert_json_content_type(response)



def test_case_29_get_statistic_is_idempotent(session, base_url, create_valid_item):
    created = create_valid_item(name="Statistic idempotency item", price=222, likes=12, view_count=34, contacts=5)

    first_response = get_statistic(session, base_url, created["id"])
    second_response = get_statistic(session, base_url, created["id"])

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.json() == second_response.json()



def test_case_30_post_get_item_and_get_statistic_are_consistent(session, base_url, create_item, seller_id):
    payload = build_item_payload(seller_id, "PlayStation 5", 55000, 7, 88, 4)
    create_response = create_item(payload)

    assert create_response.status_code == 200
    item_id = extract_created_id(create_response)

    item_response = get_item_by_id(session, base_url, item_id)
    statistic_response = get_statistic(session, base_url, item_id)

    assert item_response.status_code == 200
    assert statistic_response.status_code == 200

    item = item_response.json()[0]
    stats = statistic_response.json()

    assert item["sellerId"] == seller_id
    assert item["name"] == payload["name"]
    assert item["price"] == payload["price"]
    assert item["statistics"] == payload["statistics"]
    assert stats[0]["likes"] == payload["statistics"]["likes"]
    assert stats[0]["viewCount"] == payload["statistics"]["viewCount"]
    assert stats[0]["contacts"] == payload["statistics"]["contacts"]
