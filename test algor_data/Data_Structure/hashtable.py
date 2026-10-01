from pathlib import Path
import sys

TEST_ROOT = Path(__file__).resolve().parents[1]
if str(TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(TEST_ROOT))

from Models.project import Project


class HashNode:

    def __init__(self, project):
        self.project = project
        self.next = None


class BorrowedList:

    def __init__(self, size=101):
        self.size = size
        self.table = [None] * size
        self.count = 0

    def _hash(self, project_id):
        total = 0
        for char in project_id:
            total += ord(char)
        return total % self.size

    def insert(self, project):
        index = self._hash(project.project_id)
        new_node = HashNode(project)
        if self.table[index] is None:
            self.table[index] = new_node
        else:
            new_node.next = self.table[index]
            self.table[index] = new_node
        self.count += 1

    def search_by_project_id(self, project_id):
        index = self._hash(project_id)
        current = self.table[index]
        while current is not None:
            if current.project.project_id == project_id:
                return current.project
            current = current.next
        return None

    def search_by_project_name(self, project_name):
        results = []
        for bucket in self.table:
            current = bucket
            while current is not None:
                if current.project.project_name == project_name:
                    results.append(current.project)
                current = current.next
        return results

    def delete(self, project_id):
        index = self._hash(project_id)
        current = self.table[index]
        previous = None
        while current is not None:
            if current.project.project_id == project_id:
                if previous is None:
                    self.table[index] = current.next
                else:
                    previous.next = current.next
                self.count -= 1
                return current.project
            previous = current
            current = current.next
        return None

    def display(self):
        print("Borrowed List Hash Table")
        for i in range(self.size):
            current = self.table[i]
            if current is not None:
                print(f"Bucket {i}:", end=" ")
                while current is not None:
                    print(current.project.project_id, end=" -> ")
                    current = current.next
                print("None")


class ItemNode:

    def __init__(self, item_name, quantity):
        self.item_name = item_name
        self.quantity = quantity
        self.reserved = 0
        self.next = None


class InventoryTable:

    def __init__(self, size=101):
        self.size = size
        self.table = [None] * size
        self.count = 0

    def _hash(self, item_name):
        total = 0
        for char in item_name:
            total += ord(char)
        return total % self.size

    def insert_item(self, item_name, quantity):
        index = self._hash(item_name)
        current = self.table[index]

        while current is not None:
            if current.item_name == item_name:
                current.quantity = quantity
                return
            current = current.next

        new_node = ItemNode(item_name, quantity)
        new_node.next = self.table[index]
        self.table[index] = new_node
        self.count += 1

    def search_item(self, item_name):
        index = self._hash(item_name)
        current = self.table[index]

        while current is not None:
            if current.item_name == item_name:
                return current
            current = current.next

        return None

    def check_availability(self, requested_items):
        for item_name, quantity in requested_items.items():
            item = self.search_item(item_name)

            if item is None:
                return False

            available = item.quantity - item.reserved

            if available < quantity:
                return False

        return True

    def find_missing_items(self, requested_items):
        missing_items = {}

        for item_name, quantity in requested_items.items():
            item = self.search_item(item_name)

            if item is None:
                missing_items[item_name] = quantity
            else:
                available = item.quantity - item.reserved

                if available < quantity:
                    missing_items[item_name] = quantity - available

        return missing_items

    def reserve_items(self, requested_items):
        if not self.check_availability(requested_items):
            return False

        for item_name, quantity in requested_items.items():
            item = self.search_item(item_name)
            item.reserved += quantity

        return True

    def borrow_items(self, requested_items):
        for item_name, quantity in requested_items.items():
            item = self.search_item(item_name)

            if item is None:
                return False

            if item.reserved < quantity:
                return False

        for item_name, quantity in requested_items.items():
            item = self.search_item(item_name)
            item.quantity -= quantity
            item.reserved -= quantity

        return True

    def return_items(self, returned_items):
        for item_name, quantity in returned_items.items():
            item = self.search_item(item_name)

            if item is not None:
                item.quantity += quantity
            else:
                self.insert_item(item_name, quantity)

    def display(self):
        print("Inventory Hash Table")
        for i in range(self.size):
            current = self.table[i]
            if current is not None:
                print(f"Bucket {i}:", end=" ")
                while current is not None:
                    available = current.quantity - current.reserved
                    print(
                        f"{current.item_name} "
                        f"(Stock={current.quantity}, "
                        f"Reserved={current.reserved}, "
                        f"Available={available})",
                        end=" -> "
                    )
                    current = current.next
                print("None")


# Borrowed project testing
# Item names and quantities below are based on real rows in data/app.db.
p1 = Project(
    "P0001",
    "66000001",
    "Alice",
    "Robot Arm",
    "alice@example.com",
    "2026-10-05",
    {"Screw driver set": 2, "Current Sensor ACS712T ELC-20A": 1},
    1
)

p2 = Project(
    "P0002",
    "66000002",
    "Bob",
    "Smart Car",
    "bob@example.com",
    "2026-10-06",
    {"Wireless HDMI Extender Kits": 1},
    2
)

p3 = Project(
    "P0003",
    "66000003",
    "Charlie",
    "Drone",
    "charlie@example.com",
    "2026-10-07",
    {"Current sensor (ACS712)": 1},
    3
)

p4 = Project(
    "P0004",
    "66000004",
    "David",
    "Robot Arm",
    "david@example.com",
    "2026-10-10",
    {"Form2 3D Printer": 1},
    4
)

Borrowed = BorrowedList()
Borrowed.insert(p1)
Borrowed.insert(p2)
Borrowed.insert(p3)
Borrowed.insert(p4)
Borrowed.display()

# testing borrowed hash table
project_name = input("Enter a project name: ")
print(f"Searching for project name: {project_name}")
result = Borrowed.search_by_project_name(project_name)
if result:
    for project in result:
        print(project)
else:
    print("No projects found with that name.")

print("\nDeleting P0002:")
deleted = Borrowed.delete("P0002")

if deleted is not None:
    print("Deleted:")
    print(deleted)
else:
    print("Project not found.")

print("\nDisplaying after deletion:")
Borrowed.display()

project_id = input("Enter a project ID: ")
print(f"Searching for project ID: {project_id}")
result = Borrowed.search_by_project_id(project_id)
if result is not None:
    print(result)
else:
    print("Project not found.")


# Inventory hash table testing
# These are real item names and live quantities read from data/app.db.
Inventory = InventoryTable()
Inventory.insert_item("Screw driver set", 419)
Inventory.insert_item("Current Sensor ACS712T ELC-20A", 16)
Inventory.insert_item("Current sensor (ACS712)", 1)
Inventory.insert_item("Form2 3D Printer", 1)
Inventory.insert_item("Wireless HDMI Extender", 1)
Inventory.insert_item("Wireless HDMI Extender Kits", 2)

print("\nOriginal Inventory:")
Inventory.display()

print("\nSearching for Screw driver set:")
result = Inventory.search_item("Screw driver set")
if result is not None:
    print(result.item_name, result.quantity)
else:
    print("Item not found.")

requested_items = {
    "Screw driver set": 2,
    "Current Sensor ACS712T ELC-20A": 1
}

print("\nChecking availability:")
if Inventory.check_availability(requested_items):
    print("All items are available.")
else:
    print("Some items are unavailable.")

print("\nReserving items:")
Inventory.reserve_items(requested_items)
Inventory.display()

print("\nStudent collects items:")
Inventory.borrow_items(requested_items)
Inventory.display()

print("\nStudent returns items:")
returned_items = {
    "Screw driver set": 2,
    "Current Sensor ACS712T ELC-20A": 1
}
Inventory.return_items(returned_items)
Inventory.display()

print("\nChecking shortage:")
requested_items = {
    "Form2 3D Printer": 2,
    "Wireless HDMI Extender Kits": 3
}

missing_items = Inventory.find_missing_items(requested_items)
if missing_items:
    for item_name, quantity in missing_items.items():
        print(item_name, "short by", quantity)
else:
    print("No missing items.")

