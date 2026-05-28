from models.dbo import DBO

class Roles(DBO):
    def __init__(self, db, ID=None):
        fields = [
            "ID",
            "Name",
            "Author",
            "Created_date",
            "Last_editor",
            "Last_change",
            "Change_cnt",
        ]

        super().__init__(db, table_name="Roles", fields=fields, pk="ID")

        if ID is not None:
            self.load(ID)