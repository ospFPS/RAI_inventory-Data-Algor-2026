from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.inventory import InventoryCatalog
from Models.item import Item

EXCEL_PATH = PROJECT_ROOT / 'backend' / 'db' / 'Database_inven_RAI.xlsx'


def load_mock_items():
    catalog = InventoryCatalog()
    catalog.load_xlsx(EXCEL_PATH)
    return [Item(item.type, item.item_name, item.live_qty) for item in catalog.all_items()]


def mock_stock(*item_names):
    items = load_mock_items()
    result = {}
    for name in item_names:
        matches = [item for item in items if item.item_name == name]
        if len(matches) != 1:
            raise ValueError(f'Expected one Excel entry for {name!r}, found {len(matches)}')
        result[name] = matches[0].quantity
    return result
