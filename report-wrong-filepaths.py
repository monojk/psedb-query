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

def main():
    database = r"C:\ProgramData\Adobe\Elements Organizer\Catalogs\Gemeinsamer Katalog\catalog.pse17db"
    filepath = r"/Public/Public Pictures/"

    database = r"C:\ProgramData\Adobe\Elements Organizer\Catalogs\Joachims Katalog\catalog.pse17db"
    filepath = r"/Joachim/Pictures/"

    print(database)

    # create a database connection
    conn = create_connection(database)
    with conn:
        volume_id = get_correct_volume_id(conn)
        #print(volume_id)

        cur = conn.cursor()
        cur.execute("SELECT id, full_filepath, volume_id FROM media_table")
        for row in cur.fetchall():
            if row[2] != volume_id :
                print(str(row[0]) + " " + str(row[2]) + " " + row[1])
            if not str(row[1]).startswith(filepath):
                print(str(row[0]) + " " + row[1])


if __name__ == '__main__':
    main()
