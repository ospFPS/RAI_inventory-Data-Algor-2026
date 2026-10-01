from pathlib import Path
import sys

TEST_ROOT = Path(__file__).resolve().parents[1]
if str(TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(TEST_ROOT))

from Models.damage import DamageItem


class DamageNode:

    def __init__(self, damage):
        self.damage = damage
        self.next = None


class DamageList:

    def __init__(self):
        self.head = None
        self.tail = None
        self.count = 0

    def insert(self, damage):
        new_node = DamageNode(damage)

        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node

        self.count += 1

    def display(self):
        if self.head is None:
            print("Damage List is empty.")
            return

        current = self.head

        print("HEAD")
        print(" |")
        print(" V")

        while current is not None:
            print(current.damage)
            print(" |")
            print(" V")
            current = current.next

        print("NULL")

    def search_by_project_id(self, project_id):
        results = []
        current = self.head

        while current is not None:
            if current.damage.project_id == project_id:
                results.append(current.damage)

            current = current.next

        return results


# For testing
# Real item names are used from data/app.db.
d1 = DamageItem(
    "Form2 3D Printer",
    "P0001",
    "Build plate is damaged",
    "2026-10-10"
)

d2 = DamageItem(
    "Current sensor (ACS712)",
    "P0002",
    "Sensor gives incorrect reading",
    "2026-10-11"
)

d3 = DamageItem(
    "Wireless HDMI Extender",
    "P0003",
    "No video signal",
    "2026-10-12"
)


Damaged = DamageList()

Damaged.insert(d1)
Damaged.insert(d2)
Damaged.insert(d3)


print("Damage List:")
Damaged.display()


print("\nTotal damaged records:")
print(Damaged.count)


project_id = input("\nEnter a project ID: ")
print(f"Searching damage records for: {project_id}")

result = Damaged.search_by_project_id(
    project_id
)

if result:
    for damage in result:
        print(damage)
else:
    print("No damaged items found for this project.")
