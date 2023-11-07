import sqlite3
from sqlite3 import Error
from collections import defaultdict


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
    cur.execute("SELECT id, drive_path_if_builtin from volume_table")
    for row in cur.fetchall():
        table[row[0]] = row[1]
    return table


def get_place_alias_name_id(conn):      # returns description_id for place alias
    cur = conn.cursor()
    cur.execute("SELECT id FROM metadata_description_table WHERE identifier=?", ("pse:place_alias_name",))
    this_id = None
    for row in cur.fetchall():
        this_id = row[0]
    return this_id


def get_metadata_string_table_dict(conn):     # returns dict of all metadata_ids with value for place alias
    table = {}
    cur = conn.cursor()
    place_alias_name_id = get_place_alias_name_id(conn)
    # print(place_alias_name_id)
    cur.execute("SELECT id, value FROM metadata_string_table WHERE description_id=?", (place_alias_name_id,))
    for row in cur.fetchall():
        table[row[0]] = row[1]
    return table


def get_tag_to_metadata_table_dict(conn):   # this dict maps the metadata_id to the tag_id
    table = {}
    cur = conn.cursor()
    cur.execute("SELECT tag_id, metadata_id FROM tag_to_metadata_table")
    for row in cur.fetchall():
        table[row[1]] = row[0]
    return table


def get_user_place_dict(conn):
    metadata_string_dict = get_metadata_string_table_dict(conn)         # metadata_ids that describe place aliases
    # print(metadata_string_dict)
    tag_to_metadata_table_dict = get_tag_to_metadata_table_dict(conn)   # metadata_id -> tag_id
    table = {}
    names = {}
    parents = {}
    cur = conn.cursor()
    cur.execute("SELECT id, name, parent_id FROM tag_table WHERE type_name=?", ("user_place",))
    for row in cur.fetchall():
        names[row[0]] = row[1]
        parents[row[0]] = row[2]
        # print(names[row[0]])
    for tag_id in names:
        parent_id = parents[tag_id]
        name = names[tag_id]
        while True:
            if parent_id in names:
                name = f"{names[parent_id]} / {name}"
                parent_id = parents[parent_id]
            else:
                break
        # print(name)
        table[tag_id] = name
        # search for the alias
        for metadata_id, this_tag_id in tag_to_metadata_table_dict.items():
            if tag_id == this_tag_id:
                if metadata_id in metadata_string_dict:
                    # print(f"{tag_id} -> {metadata_id}")
                    table[tag_id] = f"{name} / {metadata_string_dict[metadata_id]}"
                    # print(table[tag_id])
                    break
    return table


def get_tag_to_media_dict(conn):
    table = defaultdict(list)
    cur = conn.cursor()
    cur.execute("SELECT media_id, tag_id FROM tag_to_media_table")
    for row in cur.fetchall():
        table[row[1]].append(row[0])
    return table


def main():

    public = True
    reportPath = fr"C:\Users\jkein\Meine Ablage\Photos"
    if public:
        database = r"C:\Users\jkein\Adobe_PSE_Catalogs\Gemeinsamer Katalog 2\catalog.pse20db"
        reportFileD = fr"{reportPath}/GemeinsamerKatalog_Orte_Detail.txt"
        reportFile  = fr"{reportPath}/GemeinsamerKatalog_Orte.txt"
    else:
        database = r"C:\Users\jkein\Adobe_PSE_Catalogs\Joachims Katalog 3\catalog.pse20db"
        reportFileD = fr"{reportPath}/JoachimsKatalog_Orte_Detail.txt"
        reportFile  = fr"{reportPath}/JoachimsKatalog_Orte.txt"

    f  = open(reportFile,  'w', encoding="utf-8")
    fD = open(reportFileD, 'w', encoding="utf-8")
    f.write(database + "\n")
    fD.write(database+ "\n")
    print(database)

    # create a database connection
    conn = create_connection(database)
    with conn:
        cur = conn.cursor()
        volume_ids_dict = get_volume_ids(conn)

        user_place_id_dict = get_user_place_dict(conn)
        tag_to_media_dict = get_tag_to_media_dict(conn)
        for tag_id in sorted(user_place_id_dict, key=user_place_id_dict.get):
            f.write(user_place_id_dict[tag_id] + "\n")
            fD.write(user_place_id_dict[tag_id] + "\n")
            print(user_place_id_dict[tag_id])
            FilePathsDict = defaultdict(list)
            for media_id in tag_to_media_dict[tag_id]:
                typeVar = media_id
                #print(media_id)
                cur.execute("SELECT id, full_filepath, volume_id from media_table WHERE id=?", (typeVar,))
                for row in cur.fetchall():
                    file_path = volume_ids_dict[row[2]] + row[1]
                    [path, name] = file_path.rsplit('/',1)
                    FilePathsDict[path].append(name)
            for path in sorted(FilePathsDict):
                f.write(f"  {path}\n")
                fD.write(f"  {path}\n")
                for name in sorted(FilePathsDict[path]):
                    fD.write(f"    {name}\n")

    f.close()
    fD.close()


if __name__ == '__main__':
    main()
