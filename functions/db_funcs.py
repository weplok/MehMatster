import sqlite3


def create_user(db_code: str, id: int, name: str, course: str = None, group: str = None) -> bool:
    """
    :param db_code: vk - БД юзеров ВК, tg - БД юзеров ТГ
    :param id: Уникальный цифровой id юзера в мессенджере
    :param name: Имя
    :param course: Курс (напр. Бакалавриат, 1 курс)
    :param group: Группа (напр. ПМИ, 1 группа)
    :return:
    """
    if db_code not in ["vk", "tg"]:
        return False
    con = sqlite3.connect(f"db/{db_code}.sqlite3")
    cur = con.cursor()
    if course is not None:
        course = cur.execute("""SELECT id FROM courses WHERE course == ?""", (course,)).fetchone()[0]
    if group is not None:
        group = cur.execute("""SELECT id FROM groups WHERE groupa == ?""", (group,)).fetchone()[0]
        is_abitur = False
    else:
        is_abitur = True
    try:
        cur.execute("""INSERT INTO users (id, name, course, groupa, is_abitur) VALUES (?, ?, ?, ?, ?)""",
                    (id, name, course, group, is_abitur))
    except sqlite3.IntegrityError:
        con.close()
        return False
    con.commit()
    con.close()
    return True
