"""Operation counting for the benchmarks (section 11 of the brief):
"counts operations (comparisons/shifts/probes, not just wall time)".

Counted wraps a value so every comparison it takes part in (<, <=, >,
>=, ==, !=) ticks a shared Counter -- this lets the *real*,
unmodified ds/heap.py, algo/binary_search.py and algo/merge_sort.py
code be benchmarked for comparison counts without adding any
instrumentation to the graded algorithm code itself. Shifts (array
element moves) and probes (hash chain steps) are counted directly by
the benchmark code instead, since those aren't expressed as Python
comparisons.
"""


class Counter:
    __slots__ = ("comparisons", "shifts", "probes")

    def __init__(self):
        self.comparisons = 0
        self.shifts = 0
        self.probes = 0

    def reset(self) -> None:
        self.comparisons = self.shifts = self.probes = 0


class Counted:
    """Wraps a comparable value; every comparison ticks counter.comparisons."""

    __slots__ = ("value", "counter")

    def __init__(self, value, counter: Counter):
        self.value = value
        self.counter = counter

    @staticmethod
    def _unwrap(other):
        return other.value if isinstance(other, Counted) else other

    def __lt__(self, other):
        self.counter.comparisons += 1
        return self.value < self._unwrap(other)

    def __le__(self, other):
        self.counter.comparisons += 1
        return self.value <= self._unwrap(other)

    def __gt__(self, other):
        self.counter.comparisons += 1
        return self.value > self._unwrap(other)

    def __ge__(self, other):
        self.counter.comparisons += 1
        return self.value >= self._unwrap(other)

    def __eq__(self, other):
        self.counter.comparisons += 1
        return self.value == self._unwrap(other)

    def __ne__(self, other):
        self.counter.comparisons += 1
        return self.value != self._unwrap(other)

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return f"Counted({self.value!r})"
