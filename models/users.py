from models.dbo import DBO

class Users(DBO):
    def __init__(self, db, ID=None):
        fields = [
            "ID",
            "Username",
            "Password",
            "HashType",
            "UserRoleID",
            "Author",
            "Created_date",
            "Last_editor",
            "Last_change",
            "Change_cnt",
        ]

        super().__init__(db, table_name="Users", fields=fields, pk="ID")

        if ID is not None:
            self.load(ID)
    
    @classmethod
    def find_by_username(cls, db, username):
        query = 'SELECT * FROM "Users" WHERE "Username" = ?'
        row = db.fetchone(query, (username,))

        if row is None:
            return None

        obj = cls(db)

        for field in obj.attributes["fields"]:
            setattr(obj, field, row[field])

        return obj