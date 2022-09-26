import datetime
import sqlite3
from sqlite3 import Error
from collections import defaultdict
try:
    import exifread
except ImportError:
    exifread = None

"""
    get_date_ids      metadata_description_table:   data_type=date_time_type    id  ->  identifier
                                                                                2079    xmp:CreateDate
    get_metadata_ids  media_to_metadata_table:      media_id -> metadata_id

    get_metadata_2_date_time_dict    metadata_date_time_table:   description_id=2079    id   -> value
                                                                                        2080    19941231T230000
    get_media_id_2_date_time_dict    media_to_metadata_table:    media_id (-> metadata_id) -> date_time
"""


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def get_date_ids(conn):
    cur = conn.cursor()
    # pse:TagDate   pse:FileDateOriginal   pse:FileDate   pse:LastOrganizerModifiedTime   xmp:CreateDate
    typeVar = "date_time_type"
    table = {}
    cur.execute("SELECT id,identifier from metadata_description_table WHERE data_type=?", (typeVar,))
    res = cur.fetchall()
    for i in res:
        if i[1] == "xmp:CreateDate":
            table[i[0]] = i[1]
    return table


def get_metadata_ids(conn, media_id):
    cur = conn.cursor()
    cur.execute("SELECT metadata_id from media_to_metadata_table WHERE media_id=?", (media_id,))
    res = cur.fetchall()
    return [i[0] for i in res]


def get_metadata_2_date_time_dict(conn, date_id):
    table = {}
    # print(date_id_dict)
    # get dict key by dict value
    # date_id = list(date_id_dict.keys())[list(date_id_dict.values()).index("xmp:CreateDate")]
    cur = conn.cursor()
    cur.execute("SELECT id,value from metadata_date_time_table WHERE description_id=?", (date_id,))
    res = cur.fetchall()
    for i in res:
        table[i[0]] = i[1]
    return table


def get_media_id_2_date_time_dict(conn):
    # 2 dimensional table:   [media_id][date_type] ->
    table = defaultdict(dict)
    date_id_dict = get_date_ids(conn)
    for date_id in date_id_dict:
        date_type = date_id_dict[date_id]
        metadata_2_date_time_dict = get_metadata_2_date_time_dict(conn, date_id)
        cur = conn.cursor()
        cur.execute("SELECT media_id,metadata_id from media_to_metadata_table")
        res = cur.fetchall()
        for i in res:
            if i[1] in metadata_2_date_time_dict:
                table[i[0]][date_type] = metadata_2_date_time_dict[i[1]]
    return table


def get_location_tags(conn):
    cur = conn.cursor()
    typeVar = "user_place"
    cur.execute("SELECT * from tag_table WHERE type_name=?", (typeVar,))
    res = cur.fetchall()
    return [i[0] for i in res]


def get_volume_ids(conn):
    cur = conn.cursor()
    table = {}
    cur.execute("SELECT id,drive_path_if_builtin from volume_table")
    for row in cur.fetchall():
        table[row[0]] = row[1]
    return table


def main():
    database = r"C:\ProgramData\Adobe\Elements Organizer\Catalogs\Gemeinsamer Katalog 2\catalog.pse20db"
    # database = r"C:\ProgramData\Adobe\Elements Organizer\Catalogs\Joachims Katalog 3\catalog.pse20db"

    print(database)

    # create a database connection
    conn = create_connection(database)
    with conn:
        location_tag_list = get_location_tags(conn)
        # print(location_tags)
        location_tag_dict = dict.fromkeys(location_tag_list, 1)
        # print(location_dict)

        volume_ids_dict = get_volume_ids(conn)
        media_id_2_date_time_dict = get_media_id_2_date_time_dict(conn)

        media_dict = {}                         # keep track which media has a location tag or not
        cur = conn.cursor()
        cur.execute("SELECT media_id, tag_id FROM tag_to_media_table")
        for row in cur.fetchall():
            if not row[0] in media_dict.keys():
                media_dict[row[0]] = 0          # media listed, not yet a location_tag
            if row[1] in location_tag_dict:
                media_dict[row[0]] = row[1]     # media has a location_tag

        missing_dict = {}
        for media_id in media_dict:
            if media_dict[media_id] == 0:
                typeVar = media_id
                cur.execute("SELECT id, full_filepath, volume_id from media_table WHERE id=?", (typeVar,))
                for row in cur.fetchall():
                    file_path = volume_ids_dict[row[2]] + row[1]
                    # print(file_path)
                    if file_path[0] != "/":
                        missing_dict[file_path] = media_id

        for name in sorted(missing_dict):
            media_id = missing_dict[name]
            # date_type = "xmp:CreateDate"
            res = name
            if media_id in media_id_2_date_time_dict:
                for date_type in media_id_2_date_time_dict[media_id]:
                    dt = media_id_2_date_time_dict[media_id][date_type]
                    dt = datetime.datetime.strptime(dt, '%Y%m%dT%H%M%S').strftime('%d.%m.%Y %H:%M')
                    res += "  " + dt
                    # res += "  " + date_type + "->" + dt
            elif exifread:
                # Open image file for reading (binary mode)
                f = open(name, 'rb')
                # Return Exif tags
                tags = exifread.process_file(f, details=False)
                # for tag in tags.keys():
                #    print("Key: %s, Value: %s" % (tag, tags[tag]))
                # if 'EXIF DateTimeOriginal' in tags:
                dt = ''
                for tag in tags.keys():
                    if "EXIF Date" in "%s" % tag:
                        dt += "%s->%s  " % (tag, tags[tag])        # ASCII to string
                res += "  " + dt
            print(res)


if __name__ == '__main__':
    main()
