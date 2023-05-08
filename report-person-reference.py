import sqlite3
from sqlite3 import Error
from collections import defaultdict
from datetime import datetime


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def get_volume_ids(conn):
    cur = conn.cursor()
    table = {}
    cur.execute("SELECT id, drive_path_if_builtin from volume_table WHERE type!=?", ("no_drive",))
    for row in cur.fetchall():
        table[row[0]] = row[1]
    return table


def get_tag_to_media_dict(conn):
    cur = conn.cursor()
    table = defaultdict(list)
    cur.execute("SELECT media_id, tag_id from tag_to_media_table")
    for row in cur.fetchall():
        if row[0] in table:
            table[row[0]].append(row[1])
        else:
            table[row[0]] = [row[1]]
    #print(table)
    return table


def get_tag_person_dict(conn):
    table = {}
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM tag_table WHERE type_name=?", ("user_person",))
    for row in cur.fetchall():
        table[row[0]] = row[1]
    return table


def get_path_to_media_id_dict(conn):
    table = {}
    volume_ids_dict = get_volume_ids(conn)
    cur = conn.cursor()
    cur.execute("SELECT id, full_filepath, volume_id from media_table")
    for row in cur.fetchall():
        if row[2] in volume_ids_dict:
            file_path = volume_ids_dict[row[2]] + row[1]
            table[file_path] = row[0]
    return table


def main():
    now = datetime.now()
    d = now.strftime("%Y_%m_%d")

    # database = r"C:\Users\jkein\Adobe_PSE_Catalogs\Gemeinsamer Katalog 2\catalog.pse20db"
    # reportFile = fr"C:\Users\jkein\Dropbox\Photos/GemeinsamerKatalog_Personen_{d}.txt"

    database = r"C:\Users\jkein\Adobe_PSE_Catalogs\Joachims Katalog 3\catalog.pse20db"
    reportFile = fr"C:\Users\jkein\Dropbox\Photos/JoachimsKatalog_Personen_{d}.txt"

    f = open(reportFile, 'w', encoding="utf-8")
    f.write(database+"\n")
    print(database)

    # create a database connection
    conn = create_connection(database)
    with conn:
        cur = conn.cursor()
        media_to_tag_dict = get_tag_to_media_dict(conn)
        # print(media_to_tag_dict)
        person_id_dict = get_tag_person_dict(conn)
        # print(person_id_dict)
        media_id_dict = get_path_to_media_id_dict(conn)
        cur.execute("SELECT id, full_filepath, volume_id from media_table")
        for file_path in sorted(media_id_dict):
            media_id = media_id_dict[file_path]
            printFileName = True
            for tag_id in media_to_tag_dict[media_id]:
                if tag_id in person_id_dict:
                    person = person_id_dict[tag_id]
                    if printFileName:
                        f.write(f"{file_path}\n")
                        printFileName = False
                    f.write(f"    {person}\n")

    f.close()
    print(f"report file: {reportFile}")


if __name__ == '__main__':
    main()
