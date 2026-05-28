from models.dbo import DBO

class Permissions(DBO):
    def __init__(self, db, ID=None):
        fields = [
            "ID",
            "Name",
            "RoleID",
            "Author",
            "Created_date",
            "Last_editor",
            "Last_change",
            "Change_cnt",
        ]

        super().__init__(db, table_name="Permissions", fields=fields, pk="ID")

        if ID is not None:
            self.load(ID)