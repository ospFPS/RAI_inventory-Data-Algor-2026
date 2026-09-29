import random

import pytest

from ds.hashtable import HashTable, fnv1a_hash


def test_put_get_basic():
    t = HashTable()
    t.put("relay-5v", 10)
    t.put("relay-12v", 4)
    assert t.get("relay-5v") == 10
    assert t.get("relay-12v") == 4
    assert t.get("missing") is None
    assert t.get("missing", "default") == "default"
    assert len(t) == 2


def test_put_overwrites_existing_key():
    t = HashTable()
    t.put("k", 1)
    t.put("k", 2)
    assert t.get("k") == 2
    assert len(t) == 1


def test_contains():
    t = HashTable()
    t.put("k", 1)
    assert "k" in t
    assert "other" not in t


def test_delete():
    t = HashTable()
    t.put("k", 1)
    assert t.delete("k") == 1
    assert "k" not in t
    assert len(t) == 0
    with pytest.raises(KeyError):
        t.delete("k")


def test_tuple_keys_for_inventory_lookup():
    t = HashTable()
    t.put(("Sensor", "Ultrasonic HC-SR04"), {"live_qty": 20})
    t.put(("Electrical", "Relay 5V"), {"live_qty": 15})
    assert t.get(("Sensor", "Ultrasonic HC-SR04"))["live_qty"] == 20
    assert t.get(("Electrical", "Relay 5V"))["live_qty"] == 15
    assert t.get(("Sensor", "Nonexistent")) is None


def test_collision_handling_with_chaining():
    # Force everything into a single bucket to exercise chaining directly.
    t = HashTable(capacity=1)
    for i in range(20):
        t.put(f"key{i}", i)
    assert t._capacity >= 1
    for i in range(20):
        assert t.get(f"key{i}") == i
    assert len(t) == 20


def test_resize_keeps_all_entries_and_load_factor_bounded():
    t = HashTable(capacity=8)
    n = 500
    for i in range(n):
        t.put(f"item-{i}", i)
    assert len(t) == n
    assert t.load_factor <= HashTable.MAX_LOAD_FACTOR
    for i in range(n):
        assert t.get(f"item-{i}") == i


def test_keys_values_items():
    t = HashTable()
    data = {"a": 1, "b": 2, "c": 3}
    for k, v in data.items():
        t.put(k, v)
    assert set(t.keys()) == set(data.keys())
    assert set(t.values()) == set(data.values())
    assert dict(t.items()) == data


def test_fnv1a_hash_deterministic_and_int():
    assert fnv1a_hash("abc") == fnv1a_hash("abc")
    assert isinstance(fnv1a_hash("abc"), int)
    assert fnv1a_hash("abc") != fnv1a_hash("abd")


def test_randomized_matches_dict_oracle():
    random.seed(7)
    t = HashTable()
    oracle = {}
    keys = [f"k{i}" for i in range(200)]
    for _ in range(2000):
        k = random.choice(keys)
        op = random.choice(["put", "get", "delete"])
        if op == "put":
            v = random.randint(0, 10_000)
            t.put(k, v)
            oracle[k] = v
        elif op == "delete":
            if k in oracle:
                assert t.delete(k) == oracle.pop(k)
            else:
                with pytest.raises(KeyError):
                    t.delete(k)
        else:
            assert t.get(k) == oracle.get(k)
    assert len(t) == len(oracle)
    for k, v in oracle.items():
        assert t.get(k) == v
