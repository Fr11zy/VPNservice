import yaml
import os

def load_schema(path):
    with open(path, "r") as f:
        schema = yaml.safe_load(f)
    return schema

def is_service_table(table_name):
    if table_name[-2:] in ("_H", "_D"):
        return True
    return False

def extract_fields(table_def):
    result = []
    for field in table_def["fields"]:
        key = list(field.keys())[0]
        result.append(key)
    return result


def build_code(class_name, table_name, fields, pk="ID"):
    fields_block = "\n".join(f'            "{field}",' for field in fields)

    code = f'''from models.dbo import DBO

class {class_name}(DBO):
    def __init__(self, db, ID=None):
        fields = [
{fields_block}
        ]

        super().__init__(db, table_name="{table_name}", fields=fields, pk="{pk}")

        if ID is not None:
            self.load(ID)
'''
    return code


def write_in_file(output_dir, table_name, code):
    os.makedirs(output_dir, exist_ok=True)
    file_name = table_name.lower() + ".py"
    path = os.path.join(output_dir, file_name)

    with open(path, "w") as f:
        f.write(code)


if __name__ == "__main__":
    schema = load_schema("config.yaml")

    for item in schema["database"]["tables"]:
        table_name, table_def = next(iter(item.items()))

        if is_service_table(table_name):
            continue

        fields = extract_fields(table_def)
        code = build_code(table_name, table_name, fields, "ID")
        write_in_file("models", table_name, code)