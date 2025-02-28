import sqlite3
from csv import DictReader


def init(db_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT
    UNIQUE
    NOT NULL,
    course TEXT
    )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT
        UNIQUE
        NOT NULL,
        groupa TEXT
        )
        """)

    con.commit()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY
    UNIQUE
    NOT NULL,
    name TEXT,
    course INTEGER REFERENCES courses (id),
    groupa INTEGER REFERENCES groups (id),
    is_abitur BOOL NOT NULL
    )
    """)

    con.commit()

    with open("functions/files/courses.tsv", "r", encoding="utf-8") as csv_file:
        reader = DictReader(csv_file, delimiter="\t")
        for row in reader:
            cur.execute("""INSERT INTO courses (course) VALUES (?)""", (row["course"],))
    with open("functions/files/groups.tsv", "r", encoding="utf-8") as csv_file:
        reader = DictReader(csv_file, delimiter="\t")
        for group in list(set([row["group"] for row in reader])):
            cur.execute("""INSERT INTO groups (groupa) VALUES (?)""", (group,))

    con.commit()
    con.close()


if __name__ == "__main__":
    with open("vk.sqlite3", "w", encoding="utf-8"):
        pass
    init("vk.sqlite3")
    with open("tg.sqlite3", "w", encoding="utf-8"):
        pass
    init("tg.sqlite3")
