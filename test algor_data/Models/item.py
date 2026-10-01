class Item:

    def __init__(self, item_type, item_name, quantity):
        self.item_type = item_type
        self.item_name = item_name
        self.quantity = quantity

    def __str__(self):
        return (
            f"{self.item_type} | "
            f"{self.item_name} | "
            f"Quantity: {self.quantity}"
        )
