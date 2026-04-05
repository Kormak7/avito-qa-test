from conftest import (
    assert_json_content_type,
    assert_item_schema,
    build_item_payload,
    extract_created_id,
    get_item_by_id,
    get_items_by_seller,
    get_statistic,
)


def test_case_01_successful_create_item(session, base_url, create_item, seller_id):
    payload = build_item_payload(seller_id, "iPhone 13", 65000, 10, 150, 3)
    response = create_item(payload)

    assert response.status_code == 200
    assert_json_content_type(response)
    assert extract_created_id(response)



def test_case_02_create_same_item_twice(create_item, seller_id):
    payload = build_item_payload(seller_id, "MacBook Air", 99000, 5, 40, 1)

    first = create_item(payload)
    second = create_item(payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert extract_created_id(first) != extract_created_id(second)



def test_case_03_same_data_different_sellers(create_item, seller_id, second_seller_id):
    payload_1 = build_item_payload(seller_id, "MacBook Air", 99000, 5, 40, 1)
    payload_2 = build_item_payload(second_seller_id, "MacBook Air", 99000, 5, 40, 1)

    first = create_item(payload_1)
    second = create_item(payload_2)

    assert first.status_code == 200
    assert second.status_code == 200
    assert extract_created_id(first) != extract_created_id(second)



def test_case_04_create_with_min_seller_id(create_item):
    response = create_item(build_item_payload(111111, "Минимальный sellerId", 1, 1, 1, 1))

    assert response.status_code == 200
    assert extract_created_id(response)



def test_case_05_create_with_max_seller_id(create_item):
    response = create_item(build_item_payload(999999, "Максимальный sellerId", 1, 1, 1, 1))

    assert response.status_code == 200
    assert extract_created_id(response)



def test_case_06_create_with_seller_id_field_name(create_item, seller_id):
    payload = {
        "sellerId": seller_id,
        "name": "Wrong seller field",
        "price": 100,
        "statistics": {"likes": 1, "viewCount": 1, "contacts": 1},
    }

    response = create_item(payload)

    assert response.status_code == 200
    assert extract_created_id(response)



def test_case_07_create_without_name(create_item, seller_id):
    payload = {
        "sellerID": seller_id,
        "price": 100,
        "statistics": {"likes": 1, "viewCount": 1, "contacts": 1},
    }

    response = create_item(payload)

    assert response.status_code == 400



def test_case_08_create_without_price(create_item, seller_id):
    payload = {
        "sellerID": seller_id,
        "name": "No price",
        "statistics": {"likes": 1, "viewCount": 1, "contacts": 1},
    }

    response = create_item(payload)

    assert response.status_code == 400



def test_case_09_create_without_statistics(create_item, seller_id):
    payload = {
        "sellerID": seller_id,
        "name": "No statistics",
        "price": 100,
    }

    response = create_item(payload)

    assert response.status_code == 400



def test_case_10_create_with_negative_price(create_item, seller_id):
    response = create_item(build_item_payload(seller_id, "Negative price", -1, 1, 1, 1))

    assert response.status_code == 200
    assert extract_created_id(response)



def test_case_11_create_with_zero_price(create_item, seller_id):
    response = create_item(build_item_payload(seller_id, "Zero price", 0, 1, 1, 1))

    assert response.status_code == 400



def test_case_12_create_with_float_price(create_item, seller_id):
    response = create_item(build_item_payload(seller_id, "Float price", 12.5, 1, 1, 1))

    assert response.status_code == 400



def test_case_13_create_with_string_price(create_item, seller_id):
    response = create_item(build_item_payload(seller_id, "String price", "1000", 1, 1, 1))

    assert response.status_code == 400



def test_case_14_create_with_invalid_seller_id(create_item):
    response = create_item(build_item_payload(-10, "Invalid seller id", 100, 1, 1, 1))

    assert response.status_code == 200
    assert extract_created_id(response)



def test_case_15_create_with_empty_name(create_item, seller_id):
    response = create_item(build_item_payload(seller_id, "", 100, 1, 1, 1))

    assert response.status_code == 400



def test_case_16_create_with_very_long_name(session, base_url, create_item, seller_id):
    long_name = "x" * 1000
    response = create_item(build_item_payload(seller_id, long_name, 100, 1, 1, 1))

    assert response.status_code == 200
    item_id = extract_created_id(response)

    item_response = get_item_by_id(session, base_url, item_id)
    assert item_response.status_code == 200
    item = item_response.json()[0]
    assert item["name"] == long_name
    assert_item_schema(item)



def test_case_31_unicode_and_special_characters_in_name(session, base_url, create_item, seller_id):
    name = "Смартфон Samsung — 128 ГБ, цвет: синий / Blue!"
    response = create_item(build_item_payload(seller_id, name, 45000, 7, 88, 4))

    assert response.status_code == 200
    item_id = extract_created_id(response)
    item_response = get_item_by_id(session, base_url, item_id)
    assert item_response.status_code == 200
    assert item_response.json()[0]["name"] == name



def test_case_32_successful_responses_have_json_content_type(session, base_url, create_item, seller_id):
    payload = build_item_payload(seller_id, "JSON content type", 12345, 2, 20, 1)
    create_response = create_item(payload)

    assert create_response.status_code == 200
    assert_json_content_type(create_response)

    item_id = extract_created_id(create_response)

    item_response = get_item_by_id(session, base_url, item_id)
    seller_response = get_items_by_seller(session, base_url, seller_id)
    stat_response = get_statistic(session, base_url, item_id)

    assert item_response.status_code == 200
    assert seller_response.status_code == 200
    assert stat_response.status_code == 200
    assert_json_content_type(item_response)
    assert_json_content_type(seller_response)
    assert_json_content_type(stat_response)



def test_case_33_api_response_time_is_within_sla(session, base_url, create_item, seller_id):
    payload = build_item_payload(seller_id, "Response time", 777, 3, 30, 2)
    response = create_item(payload)

    assert response.status_code == 200
    assert response.elapsed.total_seconds() <= 3

    item_id = extract_created_id(response)

    item_response = get_item_by_id(session, base_url, item_id)
    seller_response = get_items_by_seller(session, base_url, seller_id)
    stat_response = get_statistic(session, base_url, item_id)

    assert item_response.status_code == 200
    assert seller_response.status_code == 200
    assert stat_response.status_code == 200
    assert item_response.elapsed.total_seconds() <= 3
    assert seller_response.elapsed.total_seconds() <= 3
    assert stat_response.elapsed.total_seconds() <= 3



def test_case_34_mass_creation_of_items(create_item, seller_id):
    created_ids = []

    for index in range(20):
        payload = build_item_payload(seller_id, f"bulk-item-{index}", 1000 + index, index + 1, index + 2, index + 3)
        response = create_item(payload)
        assert response.status_code == 200
        created_ids.append(extract_created_id(response))

    assert len(created_ids) == 20
    assert len(set(created_ids)) == 20



def test_case_35_no_extra_fields_in_success_responses(session, base_url, create_item, seller_id):
    payload = build_item_payload(seller_id, "No extra fields", 2000, 11, 22, 3)
    create_response = create_item(payload)

    assert create_response.status_code == 200
    assert_json_content_type(create_response)

    item_id = extract_created_id(create_response)

    item_response = get_item_by_id(session, base_url, item_id)
    seller_response = get_items_by_seller(session, base_url, seller_id)
    stat_response = get_statistic(session, base_url, item_id)

    assert item_response.status_code == 200
    assert seller_response.status_code == 200
    assert stat_response.status_code == 200

    item = item_response.json()[0]
    assert set(item.keys()) >= {"id", "sellerId", "name", "price", "statistics", "createdAt"}
    assert set(item["statistics"].keys()) >= {"likes", "viewCount", "contacts"}

    for seller_item in seller_response.json():
        assert set(seller_item.keys()) >= {"id", "sellerId", "name", "price", "statistics", "createdAt"}
        assert set(seller_item["statistics"].keys()) >= {"likes", "viewCount", "contacts"}

    for statistics in stat_response.json():
        assert set(statistics.keys()) >= {"likes", "viewCount", "contacts"}
