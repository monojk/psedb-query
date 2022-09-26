import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def get_correct_volume_id(conn):
    cur = conn.cursor()
    typeVar = "D:"
    cur.execute("SELECT * from volume_table WHERE drive_path_if_builtin=?", (typeVar,))
    return cur.fetchone()[0]


def get_volume_ids(conn):
    cur = conn.cursor()
    table = {}
    cur.execute("SELECT id,drive_path_if_builtin from volume_table")
    for row in cur.fetchall():
        table[row[0]] = row[1]
    return table

def main():
    database = r"C:\ProgramData\Adobe\Elements Organizer\Catalogs\Gemeinsamer Katalog 2\catalog.pse20db"
    filepath = r"D:/Public/Public Pictures/"

    # database = r"C:\ProgramData\Adobe\Elements Organizer\Catalogs\Joachims Katalog 3\catalog.pse20db"
    # filepath = r"D:/Joachim/Pictures/"

    print(database)

    # create a database connection
    conn = create_connection(database)
    with conn:
        volume_ids_dict = get_volume_ids(conn)
        volume_id = get_correct_volume_id(conn)
        # print(volume_id)

        cur = conn.cursor()
        cur.execute("SELECT id, full_filepath, volume_id FROM media_table")
        for row in cur.fetchall():
            file = row[1]
            vol_id = row[2]
            file_path = volume_ids_dict[vol_id] + file
            if file_path[0] != "/":
                if not str(file_path).startswith(filepath):
                    print(file_path)


if __name__ == '__main__':
    main()
