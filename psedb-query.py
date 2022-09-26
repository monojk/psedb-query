import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def print_table_names_and_columns(conn):
    newline_indent = '\n   '
    cur = conn.cursor()
    result = cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    table_names = sorted(list(zip(*result))[0])
    print ("\ntables are:"+newline_indent+newline_indent.join(table_names))

    for table_name in table_names:
        result = cur.execute("PRAGMA table_info('%s')" % table_name).fetchall()
        column_names = list(zip(*result))[1]
        print (("\ncolumn names for %s:" % table_name)
                +newline_indent
                +(newline_indent.join(column_names)))


def main():
    # database = r"C:\ProgramData\Adobe\Elements Organizer\Catalogs\Gemeinsamer Katalog 2\catalog.pse20db"
    database = r"C:\ProgramData\Adobe\Elements Organizer\Catalogs\Joachims Katalog 3\catalog.pse20db"

    # create a database connection
    conn = create_connection(database)
    with conn:
        print_table_names_and_columns(conn)


if __name__ == '__main__':
    main()
