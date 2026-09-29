"""Reproduces the four complexity comparisons from section 11 of the
brief, counting real operations (comparisons/shifts/probes) rather than
just timing wall clock. Prints a table for each and saves a bar chart to
benchmarks/output/.

Run:
    python -m benchmarks.run_benchmarks
"""

import os
import random
import statistics

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from algo.binary_search import binary_search_exact
from algo.merge_sort import merge_sort
from app.inventory import InventoryCatalog
from benchmarks.baselines import (
    bubble_sort,
    hashtable_probe_lookup,
    insertion_sort,
    linear_list_lookup,
    linear_search,
    linked_list_lookup,
    quicksort,
    selection_sort,
    sorted_array_insert,
    unsorted_array_find_min,
    unsorted_array_insert,
)
from benchmarks.counters import Counted, Counter
from ds.hashtable import HashTable
from ds.heap import MinHeap
from ds.linkedlist import SinglyLinkedList

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def print_table(title: str, headers: list[str], rows: list[list]) -> None:
    print()
    print(title)
    print("-" * len(title))
    widths = [max(len(str(h)), *(len(str(r[i])) for r in rows)) for i, h in enumerate(headers)]
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*["-" * w for w in widths]))
    for row in rows:
        print(fmt.format(*row))


def save_bar_chart(path: str, title: str, labels: list[str], series: dict[str, list[float]], ylabel: str) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    n_series = len(series)
    width = 0.8 / max(n_series, 1)
    x = range(len(labels))
    for i, (name, values) in enumerate(series.items()):
        offsets = [xi + i * width for xi in x]
        ax.bar(offsets, values, width=width, label=name)
    ax.set_xticks([xi + width * (n_series - 1) / 2 for xi in x])
    ax.set_xticklabels(labels)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


# -- 1. Min-Heap vs unsorted array vs sorted array, n=75 ------------------


def benchmark_heap_vs_arrays(n: int = 75, trials: int = 15) -> None:
    heap_insert, heap_drain = [], []
    unsorted_insert, unsorted_findmin = [], []
    sorted_insert, sorted_shifts = [], []

    for _ in range(trials):
        values = random.sample(range(1, 1_000_000), n)

        c = Counter()
        heap = MinHeap(key_func=lambda item, c=c: Counted(item[1], c), id_func=lambda item: item[0])
        for i, v in enumerate(values):
            heap.push((i, v))
        heap_insert.append(c.comparisons)

        c2 = Counter()
        heap2 = MinHeap(key_func=lambda item, c=c2: Counted(item[1], c2), id_func=lambda item: item[0])
        for i, v in enumerate(values):
            heap2.push((i, v))
        c2.reset()
        while not heap2.is_empty():
            heap2.pop()
        heap_drain.append(c2.comparisons)

        c3 = Counter()
        arr = []
        for v in values:
            unsorted_array_insert(arr, v, c3)
        unsorted_insert.append(c3.comparisons)
        unsorted_array_find_min(arr, c3)
        unsorted_findmin.append(c3.comparisons - 0)  # insert contributed 0

        c4 = Counter()
        sarr = []
        for v in values:
            sorted_array_insert(sarr, v, c4)
        sorted_insert.append(c4.comparisons)
        sorted_shifts.append(c4.shifts)

    print_table(
        f"1. Min-Heap vs unsorted array vs sorted array (n={n}, {trials} trials, mean)",
        ["Structure", "Insert (comparisons)", "Insert (shifts)", "Find-min (comparisons)"],
        [
            ["Min-Heap", f"{statistics.mean(heap_insert):.1f}", "0 (in-place swaps only)", "0 (peek is O(1))"],
            ["Unsorted array", "0", "0", f"{statistics.mean(unsorted_findmin):.1f}"],
            ["Sorted array", f"{statistics.mean(sorted_insert):.1f}", f"{statistics.mean(sorted_shifts):.1f}", "0 (front is O(1))"],
        ],
    )
    print(f"   (Min-Heap: draining all {n} in priority order costs {statistics.mean(heap_drain):.1f} comparisons total)")

    save_bar_chart(
        os.path.join(OUTPUT_DIR, "heap_vs_arrays.png"),
        f"Insert cost, n={n} (mean of {trials} trials)",
        ["Min-Heap", "Unsorted array", "Sorted array"],
        {
            "Comparisons": [statistics.mean(heap_insert), 0, statistics.mean(sorted_insert)],
            "Shifts": [0, 0, statistics.mean(sorted_shifts)],
        },
        "operations per full build",
    )


# -- 2. Hash Table vs array / linked-list lookup, m=200 --------------------


def benchmark_hashtable_vs_lookup(m: int = 200, trials: int = 200) -> None:
    catalog = InventoryCatalog()
    catalog.load_csv(os.path.join(os.path.dirname(__file__), "..", "data", "inventory_seed.csv"))
    keys = [item.key for item in catalog.all_items()][:m]

    table = HashTable()
    pairs = []
    ll = SinglyLinkedList()
    for k in keys:
        table.put(k, k)
        pairs.append((k, k))
        ll.append((k, k))

    hash_probes, list_cmp, ll_cmp = [], [], []
    targets = [random.choice(keys) for _ in range(trials // 2)] + [
        ("Nonexistent", "Nonexistent") for _ in range(trials - trials // 2)
    ]
    random.shuffle(targets)

    for target in targets:
        _, probes = hashtable_probe_lookup(table, target)
        hash_probes.append(probes)

        c = Counter()
        linear_list_lookup(pairs, target, c)
        list_cmp.append(c.comparisons)

        c2 = Counter()
        linked_list_lookup(ll, target, c2)
        ll_cmp.append(c2.comparisons)

    print_table(
        f"2. Hash Table vs array/linked-list lookup (m={m}, {trials} lookups, mean/max)",
        ["Structure", "Mean probes/comparisons", "Max observed", "Load factor / chain"],
        [
            ["Hash Table", f"{statistics.mean(hash_probes):.2f}", str(max(hash_probes)), f"load factor {table.load_factor:.2f}, max chain {table.max_chain_length()}"],
            ["Array (linear scan)", f"{statistics.mean(list_cmp):.1f}", str(max(list_cmp)), "-"],
            ["Linked list (traverse)", f"{statistics.mean(ll_cmp):.1f}", str(max(ll_cmp)), "-"],
        ],
    )

    save_bar_chart(
        os.path.join(OUTPUT_DIR, "hashtable_vs_lookup.png"),
        f"Lookup cost, m={m} ({trials} lookups)",
        ["Hash Table", "Array (linear)", "Linked list"],
        {
            "Mean": [statistics.mean(hash_probes), statistics.mean(list_cmp), statistics.mean(ll_cmp)],
            "Max": [max(hash_probes), max(list_cmp), max(ll_cmp)],
        },
        "probes / comparisons per lookup",
    )


# -- 3. Binary Search vs Linear Search, m=200 -----------------------------


def benchmark_binary_vs_linear_search(m: int = 200, trials: int = 200) -> None:
    catalog = InventoryCatalog()
    catalog.load_csv(os.path.join(os.path.dirname(__file__), "..", "data", "inventory_seed.csv"))
    items = catalog.all_items()[:m]

    binary_cmp, linear_cmp = [], []
    targets = [items[random.randrange(m)].key for _ in range(trials // 2)] + [
        ("Nonexistent", "Nonexistent") for _ in range(trials - trials // 2)
    ]
    random.shuffle(targets)

    for target in targets:
        c = Counter()
        wrapped_items = [Counted(it.key, c) for it in items]
        binary_search_exact(wrapped_items, target, key_func=lambda x: x)
        binary_cmp.append(c.comparisons)

        c2 = Counter()
        linear_search(items, target, c2, key_func=lambda it: it.key)
        linear_cmp.append(c2.comparisons)

    print_table(
        f"3. Binary Search vs Linear Search (m={m}, {trials} searches, mean/max)",
        ["Algorithm", "Mean comparisons", "Max observed", "~log2(m) probes"],
        [
            ["Binary Search", f"{statistics.mean(binary_cmp):.2f}", str(max(binary_cmp)), str(m.bit_length())],
            ["Linear Search", f"{statistics.mean(linear_cmp):.1f}", str(max(linear_cmp)), str(m)],
        ],
    )

    save_bar_chart(
        os.path.join(OUTPUT_DIR, "binary_vs_linear_search.png"),
        f"Search cost, m={m} ({trials} searches)",
        ["Binary Search", "Linear Search"],
        {"Mean": [statistics.mean(binary_cmp), statistics.mean(linear_cmp)], "Max": [max(binary_cmp), max(linear_cmp)]},
        "comparisons per search",
    )


# -- 4. Merge Sort vs Selection/Bubble/Insertion/Quick Sort, n~75 ----------


def benchmark_sorts(n: int = 75, trials: int = 10) -> None:
    algos = {
        "Merge Sort": lambda arr, c: merge_sort([Counted(x, c) for x in arr], key_func=lambda x: x),
        "Bubble Sort": bubble_sort,
        "Selection Sort": selection_sort,
        "Insertion Sort": insertion_sort,
        "Quick Sort": quicksort,
    }
    totals = {name: [] for name in algos}

    for _ in range(trials):
        values = random.sample(range(1, 1_000_000), n)
        for name, fn in algos.items():
            c = Counter()
            fn(values, c)
            totals[name].append(c.comparisons)

    rows = [[name, f"{statistics.mean(v):.1f}", str(max(v)), str(min(v))] for name, v in totals.items()]
    print_table(
        f"4. Merge Sort vs baseline sorts (n={n}, {trials} trials, random input)",
        ["Algorithm", "Mean comparisons", "Max", "Min"],
        rows,
    )

    save_bar_chart(
        os.path.join(OUTPUT_DIR, "sort_comparison.png"),
        f"Sort cost, n={n} (mean of {trials} trials, random input)",
        list(algos.keys()),
        {"Mean comparisons": [statistics.mean(totals[name]) for name in algos]},
        "comparisons",
    )


def main():
    random.seed(2026)
    print("RAI Item Allocator -- DSA benchmark suite")
    print("=" * 60)
    benchmark_heap_vs_arrays()
    benchmark_hashtable_vs_lookup()
    benchmark_binary_vs_linear_search()
    benchmark_sorts()
    print()
    print(f"Charts saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
