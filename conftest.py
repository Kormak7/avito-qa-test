import pytest
import requests
from functools import partial

BASE_URL = "https://qa-internship.avito.com"
REQUEST_TIMEOUT = 10
SELLER_COUNTER = 111111
NAME_COUNTER = 1
UNUSED_SELLER_BASE = 900000000
UNUSED_SELLER_COUNTER = 0


def make_item_payload(seller_id, name, price, likes=1, view_count=1, contacts=1):
    return {
        "sellerID": seller_id,
        "name": name,
        "price": price,
        "statistics": {
            "likes": likes,
            "viewCount": view_count,
            "contacts": contacts,
        },
    }

build_item_payload = make_item_payload


def post_item(session, base_url, payload):
    return session.post(f"{base_url}/api/1/item", json=payload, timeout=REQUEST_TIMEOUT)


def create_valid_item_record(create_item_fn, seller_id, unique_name, name=None, price=1000, likes=1, view_count=1, contacts=1, current_seller_id=None):
    resolved_name = unique_name if name is None else name
    resolved_seller_id = seller_id if current_seller_id is None else current_seller_id
    payload = make_item_payload(resolved_seller_id, resolved_name, price, likes, view_count, contacts)
    response = create_item_fn(payload)
    assert response.status_code == 200, response.text
    item_id = extract_created_id(response)
    return {
        "id": item_id,
        "sellerId": resolved_seller_id,
        "name": resolved_name,
        "price": price,
        "statistics": {
            "likes": likes,
            "viewCount": view_count,
            "contacts": contacts,
        },
    }


@pytest.fixture
def base_url():
    return BASE_URL


@pytest.fixture
def session():
    client = requests.Session()
    client.headers.update({"Accept": "application/json"})
    yield client
    client.close()


@pytest.fixture
def seller_id():
    global SELLER_COUNTER
    value = SELLER_COUNTER
    SELLER_COUNTER += 1
    return value


@pytest.fixture
def second_seller_id():
    global SELLER_COUNTER
    value = SELLER_COUNTER
    SELLER_COUNTER += 1
    return value


@pytest.fixture
def unused_seller_id():
    global UNUSED_SELLER_COUNTER
    value = UNUSED_SELLER_BASE + UNUSED_SELLER_COUNTER
    UNUSED_SELLER_COUNTER += 1
    return value


@pytest.fixture
def unique_name():
    global NAME_COUNTER
    value = f"test-item-{NAME_COUNTER}"
    NAME_COUNTER += 1
    return value


@pytest.fixture
def payload_factory():
    return make_item_payload


@pytest.fixture
def create_item(session, base_url):
    return partial(post_item, session, base_url)


@pytest.fixture
def create_valid_item(create_item, seller_id, unique_name):
    return partial(
        create_valid_item_record,
        create_item,
        seller_id,
        unique_name,
    )


def extract_created_id(response):
    data = response.json()
    if isinstance(data, dict):
        status = data.get("status", "")
        if " - " in status:
            return status.rsplit(" - ", 1)[-1].strip()
        return status.strip()
    assert False, response.text


def get_item_by_id(session, base_url, item_id):
    return session.get(f"{base_url}/api/1/item/{item_id}", timeout=REQUEST_TIMEOUT)


def get_items_by_seller(session, base_url, seller_id):
    return session.get(f"{base_url}/api/1/{seller_id}/item", timeout=REQUEST_TIMEOUT)


def get_statistic(session, base_url, item_id):
    return session.get(f"{base_url}/api/1/statistic/{item_id}", timeout=REQUEST_TIMEOUT)


def assert_json_content_type(response):
    content_type = response.headers.get("Content-Type", "").lower()
    assert "application/json" in content_type, content_type


def assert_item_schema(item):
    assert isinstance(item, dict)
    assert "id" in item
    assert "sellerId" in item
    assert "name" in item
    assert "price" in item
    assert "statistics" in item
    assert "createdAt" in item
    assert isinstance(item["id"], str) and item["id"]
    assert isinstance(item["sellerId"], int)
    assert isinstance(item["name"], str)
    assert isinstance(item["price"], int)
    assert isinstance(item["statistics"], dict)
    assert "likes" in item["statistics"]
    assert "viewCount" in item["statistics"]
    assert "contacts" in item["statistics"]
    assert isinstance(item["statistics"]["likes"], int)
    assert isinstance(item["statistics"]["viewCount"], int)
    assert isinstance(item["statistics"]["contacts"], int)


def assert_statistics_schema(statistics):
    assert isinstance(statistics, dict)
    assert "likes" in statistics
    assert "viewCount" in statistics
    assert "contacts" in statistics
    assert isinstance(statistics["likes"], int)
    assert isinstance(statistics["viewCount"], int)
    assert isinstance(statistics["contacts"], int)
    assert statistics["likes"] >= 0
    assert statistics["viewCount"] >= 0
    assert statistics["contacts"] >= 0


def extract_items(response):
    data = response.json()
    assert isinstance(data, list), response.text
    return data


def find_item(items, item_id):
    for item in items:
        if item.get("id") == item_id:
            return item
    assert False, f"Item with id={item_id} not found"