def fetch_as_dict(cursor):
    columns = [col[0] for col in cursor.description]  # Tên cột
    result = []
    for row in cursor.fetchall():
        result.append(dict(zip(columns, row)))
    return result

def fetch_one_as_dict(cursor):
    columns = [col[0] for col in cursor.description]  # Tên cột
    row = cursor.fetchone()
    return dict(zip(columns, row))
