class Project:
    def __init__(self, project_id, student_id, student_name,
                 project_name, student_email, pickup_date, items, request_order):

        self.project_id = project_id
        self.student_id = student_id
        self.student_name = student_name
        self.project_name = project_name
        self.student_email = student_email
        self.pickup_date = pickup_date
        self.items = items
        self.request_order = request_order
        self.status = "MAIN_QUEUE"

    def __str__(self):
        return (
            f"{self.project_id} | "
            f"{self.project_name} | "
            f"{self.student_name} | "
            f"{self.student_email} | "
            f"Pickup: {self.pickup_date} | "
            f"Status: {self.status}"
        )