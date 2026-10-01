class DamageItem:

    def __init__(
        self,
        item_name,
        project_id,
        damage_description,
        date_returned
    ):
        self.item_name = item_name
        self.project_id = project_id
        self.damage_description = damage_description
        self.date_returned = date_returned

    def __str__(self):
        return (
            f"{self.item_name} | "
            f"Project: {self.project_id} | "
            f"Damage: {self.damage_description} | "
            f"Returned: {self.date_returned}"
        )
