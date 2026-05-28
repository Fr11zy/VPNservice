from datetime import datetime

class DBO:
    def __init__(self, db, table_name, fields, pk="ID"):
        self.db = db
        self.attributes = {
            "table_name": table_name,
            "fields": fields,
            "pk": pk
        }
        for field in fields:
            setattr(self, field, None)
    
    def load(self, pk_value):
        table_name = self.attributes["table_name"]
        pk = self.attributes["pk"]

        query = f'SELECT * FROM "{table_name}" WHERE "{pk}" = ?'
        row = self.db.fetchone(query, (pk_value,))

        if row is None:
            raise ValueError(f'Record with {pk}={pk_value} not found in table "{table_name}"')

        for field in self.attributes["fields"]:
            setattr(self, field, row[field])

    def _get_field_values(self):
        result = {}
        for field in self.attributes["fields"]:
            result[field] = getattr(self, field)
        return result
    
    def _insert_into_table(self, table_name, data):
        fields = list(data.keys())
        placeholders = ", ".join(["?"] * len(fields))
        field_names = ", ".join(f'"{field}"' for field in fields)
        values = tuple(data[field] for field in fields)

        query = f'INSERT INTO "{table_name}" ({field_names}) VALUES ({placeholders})'
        return self.db.execute(query, values)
    
    def dbInsert(self):
        data = self._get_field_values()

        data = {k: v for k, v in data.items() if v is not None}

        if self.attributes["pk"] in data and data[self.attributes["pk"]] is None:
            del data[self.attributes['pk']]

        cursor = self._insert_into_table(self.attributes["table_name"], data)
        pk = self.attributes["pk"]
        if getattr(self, pk) is None:
            setattr(self, pk, cursor.lastrowid)

    def dbUpdate(self, editor="system"):
        table_name = self.attributes["table_name"]
        history_table = f'{table_name}_H'
        pk = self.attributes["pk"]

        pk_value = getattr(self, pk)
        if pk_value is None:
            raise ValueError("Cannot update record without primary key")
        
        current_row = self.db.fetchone(
            f'SELECT * FROM "{table_name}" WHERE "{pk}" = ?',
            (pk_value,)
        )
        if current_row is None:
            raise ValueError(f'Record with {pk}={pk_value} not found in table "{table_name}"')
        
        history_data = {}
        for field in self.attributes["fields"]:
            history_data[field] = current_row[field]

        self._insert_into_table(history_table, history_data)

        if "Change_cnt" in self.attributes["fields"]:
            current_cnt = current_row["Change_cnt"]
            if current_cnt is None:
                current_cnt = 0
            self.Change_cnt = current_cnt + 1

        if "Last_change" in self.attributes["fields"]:
            self.Last_change = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if "Last_editor" in self.attributes["fields"]:
            self.Last_editor = editor

        update_fields = [field for field in self.attributes["fields"] if field != pk]
        set_clause = ", ".join(f'"{field}" = ?' for field in update_fields)
        values = tuple(getattr(self, field) for field in update_fields) + (pk_value,)

        query = f'UPDATE "{table_name}" SET {set_clause} WHERE "{pk}" = ?'
        self.db.execute(query, values)

    def dbDelete(self):
        table_name = self.attributes["table_name"]
        deleted_table = f"{table_name}_D"
        pk = self.attributes["pk"]

        pk_value = getattr(self, pk)
        if pk_value is None:
            raise ValueError("Cannot delete record without primary key")

        current_row = self.db.fetchone(
            f'SELECT * FROM "{table_name}" WHERE "{pk}" = ?',
            (pk_value,)
        )
        if current_row is None:
            raise ValueError(f'Record with {pk}={pk_value} not found in table "{table_name}"')

        deleted_data = {}
        for field in self.attributes["fields"]:
            deleted_data[field] = current_row[field]

        self._insert_into_table(deleted_table, deleted_data)

        query = f'DELETE FROM "{table_name}" WHERE "{pk}" = ?'
        self.db.execute(query, (pk_value,))