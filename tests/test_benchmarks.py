from algo.binary_search import binary_search_exact
from algo.merge_sort import merge_sort
from benchmarks.baselines import (
    bubble_sort,
    hashtable_probe_lookup,
    insertion_sort,
    linear_search,
    quicksort,
    selection_sort,
    sorted_array_insert,
    unsorted_array_find_min,
)
from benchmarks.counters import Counted, Counter
from ds.hashtable import HashTable


def test_counted_ticks_on_each_comparison_operator():
    c = Counter()
    a, b = Counted(3, c), Counted(5, c)
    assert (a < b) is True
    assert (a > b) is False
    assert (a == b) is False
    assert (a <= Counted(3, c)) is True
    assert c.comparisons == 4


def test_counted_compares_against_raw_value_too():
    c = Counter()
    a = Counted(3, c)
    assert (a < 5) is True
    assert c.comparisons == 1


def test_unsorted_array_find_min_counts_n_minus_1_comparisons():
    c = Counter()
    arr = [5, 3, 8, 1, 9]
    result = unsorted_array_find_min(arr, c)
    assert result == 1
    assert c.comparisons == len(arr) - 1


def test_sorted_array_insert_keeps_sorted_and_counts_shifts():
    c = Counter()
    arr = [1, 3, 5, 7]
    sorted_array_insert(arr, 4, c)
    assert arr == [1, 3, 4, 5, 7]
    assert c.shifts == 2  # 5 and 7 shifted right


def test_linear_search_counts_up_to_match_index():
    c = Counter()
    arr = [10, 20, 30, 40]
    idx = linear_search(arr, 30, c)
    assert idx == 2
    assert c.comparisons == 3


def test_hashtable_probe_lookup_matches_real_get():
    table = HashTable()
    for i in range(50):
        table.put(f"k{i}", i)
    value, probes = hashtable_probe_lookup(table, "k25")
    assert value == 25
    assert probes >= 1
    assert table.get("k25") == value


def test_baseline_sorts_produce_correctly_sorted_output():
    c = Counter()
    arr = [5, 3, 8, 1, 9, 2, 7]
    expected = sorted(arr)
    assert bubble_sort(arr, c) == expected
    assert selection_sort(arr, c) == expected
    assert insertion_sort(arr, c) == expected
    assert quicksort(arr, c) == expected


def test_merge_sort_with_counted_wrapper_still_sorts_correctly():
    c = Counter()
    arr = [5, 3, 8, 1, 9, 2, 7]
    result = merge_sort([Counted(x, c) for x in arr], key_func=lambda x: x)
    assert [item.value for item in result] == sorted(arr)
    assert c.comparisons > 0


def test_binary_search_with_counted_wrapper_still_finds_target():
    c = Counter()
    arr = [1, 3, 5, 7, 9, 11]
    wrapped = [Counted(x, c) for x in arr]
    idx = binary_search_exact(wrapped, 7, key_func=lambda x: x)
    assert idx == 3
    assert c.comparisons > 0
