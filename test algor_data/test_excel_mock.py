import hashlib
import os
import subprocess
import sys
import unittest
from pathlib import Path

TEST_ROOT = Path(__file__).resolve().parent
ROOT = TEST_ROOT.parent
sys.path.insert(0, str(TEST_ROOT))
sys.path.insert(0, str(ROOT))

from backend.inventory import InventoryCatalog
from mock_data import EXCEL_PATH, load_mock_items, mock_stock


class ExcelMockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.excel_sha = hashlib.sha256(EXCEL_PATH.read_bytes()).hexdigest()
        cls.database_path = ROOT / "backend" / "db" / "app.db"
        cls.db_sha = (
            hashlib.sha256(cls.database_path.read_bytes()).hexdigest()
            if cls.database_path.exists() else None
        )

    @classmethod
    def tearDownClass(cls):
        assert hashlib.sha256(EXCEL_PATH.read_bytes()).hexdigest() == cls.excel_sha
        if cls.db_sha is not None:
            assert hashlib.sha256(cls.database_path.read_bytes()).hexdigest() == cls.db_sha

    def run_demo(self, script, input_text="", expected=()):
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
        outcome = subprocess.run(
            [sys.executable, str(TEST_ROOT / script)],
            cwd=ROOT,
            input=input_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=30,
        )
        self.assertEqual(outcome.returncode, 0, outcome.stderr)
        for phrase in expected:
            self.assertIn(phrase, outcome.stdout)
        return outcome.stdout

    def test_real_excel_entries_match_production_catalog(self):
        real = InventoryCatalog()
        real.load_xlsx(EXCEL_PATH)
        samples = load_mock_items()
        from_production = {
            (item.type, item.item_name): item.live_qty
            for item in real.all_items()
        }
        from_mock = {(item.item_type, item.item_name): item.quantity for item in samples}
        self.assertEqual(from_mock, from_production)
        self.assertGreater(len(samples), 100)

    def test_mock_stock_does_not_change_source_inventory(self):
        stock = mock_stock("Form2 3D Printer", "Screw driver set")
        self.assertGreater(stock["Screw driver set"], 0)
        original = stock["Screw driver set"]
        stock["Screw driver set"] = 0
        self.assertEqual(mock_stock("Screw driver set")["Screw driver set"], original)
        with self.assertRaises(ValueError):
            mock_stock("This name is not in RAI inventory")

    def test_binary_search(self):
        qty = mock_stock("Screw driver set")["Screw driver set"]
        self.run_demo(
            "Algorithms/binary_search.py", "Tool\nScrew driver set\n",
            (f"Tool | Screw driver set | Quantity: {qty}",
             "Item found:", "Item not found.", "Binary Search checks:"),
        )

    def test_merge_sort(self):
        result = self.run_demo(
            "Algorithms/merge_sort.py",
            expected=("1 P0004", "2 P0002", "3 P0003", "4 P0001"),
        )
        self.assertLess(result.index("1 P0004"), result.index("4 P0001"))

    def test_min_heaps(self):
        starting = mock_stock("Form2 3D Printer")["Form2 3D Printer"]
        self.run_demo(
            "Algorithms/min_heaps.py",
            expected=(
                f"Form2 3D Printer = {starting}",
                "Moved to Pending Min-Heap.",
                "Mock replenishment: 2 Form2 3D Printers.",
                "Mock replenishment: 4 more Form2 3D Printers.",
                "Final Pending Min-Heap:\nHeap is empty.",
            ),
        )

    def test_hash_table(self):
        quantity = mock_stock("Screw driver set")["Screw driver set"]
        self.run_demo(
            "Data_Structure/hashtable.py", "Robot Arm\nP0001\n",
            expected=(
                f"Screw driver set (Stock={quantity}, Reserved=0",
                "Reserving items:",
                "Student collects items:",
                "Student returns items:",
                "Form2 3D Printer short by",
            ),
        )

    def test_linked_list(self):
        self.run_demo(
            "Data_Structure/linked_list.py", "P0001\n",
            expected=(
                "Form2 3D Printer | Project: P0001",
                "Current sensor (ACS712) | Project: P0002",
                "Total damaged records:\n3",
            ),
        )


if __name__ == "__main__":
    unittest.main()
