import pytest

from app.inventory import InventoryCatalog
from app.models import InventoryItem, ItemStatus

SEED_CSV = "data/inventory_seed.csv"


def small_catalog():
    # Names deliberately distinct from data/inventory_seed.csv so the
    # merge/replace tests below can tell fixture and seed data apart.
    c = InventoryCatalog()
    c.upsert(InventoryItem("Electrical", "Fixture Relay 5V", live_qty=10))
    c.upsert(InventoryItem("Electrical", "Fixture Relay 12V", live_qty=10))
    c.upsert(InventoryItem("Sensor", "Fixture Ultrasonic Sensor", live_qty=5))
    c.upsert(InventoryItem("Sensor", "Fixture IR Sensor", live_qty=1))
    return c


def test_get_and_find_exact_agree():
    c = small_catalog()
    a = c.get("Electrical", "Fixture Relay 5V")
    b = c.find_exact("Electrical", "Fixture Relay 5V")
    assert a is b
    assert c.get("Electrical", "Nonexistent") is None
    assert c.find_exact("Electrical", "Nonexistent") is None


def test_reserve_and_release():
    c = small_catalog()
    c.reserve("Electrical", "Fixture Relay 5V", 4)
    item = c.get("Electrical", "Fixture Relay 5V")
    assert item.reserved_qty == 4
    assert item.available_qty == 6
    assert item.live_qty == 10  # live untouched by reservation
    c.release_reservation("Electrical", "Fixture Relay 5V", 4)
    assert item.reserved_qty == 0
    assert item.available_qty == 10


def test_issue_reduces_live_and_clears_reservation():
    c = small_catalog()
    c.reserve("Electrical", "Fixture Relay 5V", 4)
    c.issue("Electrical", "Fixture Relay 5V", 4)
    item = c.get("Electrical", "Fixture Relay 5V")
    assert item.live_qty == 6
    assert item.reserved_qty == 0
    assert item.available_qty == 6


def test_restock_good_adds_back_to_live():
    c = small_catalog()
    c.reserve("Electrical", "Fixture Relay 5V", 4)
    c.issue("Electrical", "Fixture Relay 5V", 4)
    c.restock_good("Electrical", "Fixture Relay 5V", 4)
    item = c.get("Electrical", "Fixture Relay 5V")
    assert item.live_qty == 10
    assert item.available_qty == 10


def test_missing_item_operations_raise():
    c = small_catalog()
    with pytest.raises(KeyError):
        c.reserve("Electrical", "Nope", 1)
    with pytest.raises(KeyError):
        c.issue("Electrical", "Nope", 1)


def test_status_thresholds():
    assert InventoryItem("T", "a", live_qty=10, reserved_qty=0).status == ItemStatus.AVAILABLE
    assert InventoryItem("T", "a", live_qty=10, reserved_qty=10).status == ItemStatus.OUT_OF_STOCK
    # available=1 <= max(2, 10*0.2=2) -> low stock
    assert InventoryItem("T", "a", live_qty=10, reserved_qty=9).status == ItemStatus.LOW_STOCK


def test_search_by_name_prefix_case_insensitive():
    c = small_catalog()
    results = c.search_by_name_prefix("fixture relay")
    names = sorted(r.item_name for r in results)
    assert names == ["Fixture Relay 12V", "Fixture Relay 5V"]


def test_search_by_name_prefix_scoped_to_type():
    c = small_catalog()
    results = c.search_by_name_prefix("Fixture Ultrasonic", type_="Sensor")
    assert [r.item_name for r in results] == ["Fixture Ultrasonic Sensor"]
    assert c.search_by_name_prefix("Fixture Ultrasonic", type_="Electrical") == []


def test_search_empty_prefix_returns_all_in_scope():
    c = small_catalog()
    assert len(c.search_by_name_prefix("")) == len(c)
    assert len(c.search_by_name_prefix("", type_="Electrical")) == 2


def test_search_no_match():
    c = small_catalog()
    assert c.search_by_name_prefix("zzz") == []


def test_load_csv_seed_has_no_duplicates_and_is_sorted():
    c = InventoryCatalog()
    n = c.load_csv(SEED_CSV)
    assert n == 200
    assert len(c) == 200
    items = c.all_items()
    keys = [item.key for item in items]
    assert keys == sorted(keys)
    assert len(set(keys)) == len(keys)


def test_load_csv_replace_clears_previous():
    c = small_catalog()
    assert len(c) == 4
    c.load_csv(SEED_CSV, replace=True)
    assert len(c) == 200
    # a fixture item not present in the seed CSV must be gone after replace
    assert c.get("Sensor", "Fixture IR Sensor") is None


def test_load_csv_no_replace_merges():
    c = small_catalog()
    c.load_csv(SEED_CSV, replace=False)
    assert len(c) > 200  # 4 fixture items plus the 200 seed items
    assert c.get("Sensor", "Fixture IR Sensor") is not None


def test_types_from_seed():
    c = InventoryCatalog()
    c.load_csv(SEED_CSV)
    assert c.types() == ["Control", "Electrical", "Mechanical", "Sensor"]
