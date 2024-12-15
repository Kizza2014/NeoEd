from typing import List


def fetch_all_as_dict(cursor) -> List[dict]:
    columns = [col[0] for col in cursor.description]  # Tên cột
    result = []
    for row in cursor.fetchall():
        result.append(dict(zip(columns,row)))
    return result

def fetch_one_as_dict(cursor) -> dict | None:
    columns = [col[0] for col in cursor.description]  # Tên cột
    row = cursor.fetchone()
    if row is not None:
        return dict(zip(columns, row))
    return None