import sqlite3
import os


def get_db_path(db_code):
    db_file_name = f"{db_code}.sqlite3"
    hosting_db_path = os.path.join('/data', db_file_name)
    if os.path.isfile(hosting_db_path):
        return hosting_db_path
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, 'db', db_file_name)
        return db_path


def create_user(db_code: str, uid: int, name: str, course: str = None, group: str = None) -> bool:
    """
    :param db_code: vk - БД юзеров ВК, tg - БД юзеров ТГ
    :param uid: Уникальный цифровой id юзера в мессенджере
    :param name: Имя
    :param course: Курс (напр. Бакалавриат, 1 курс) - у абитуриента НЕ УКАЗЫВАЕТСЯ
    :param group: Группа (напр. ПМИ, 1 группа) - у абитуриента НЕ УКАЗЫВАЕТСЯ
    :return: True, если юзер создан, иначе False (неверный db_code)
    """

    if db_code not in ["vk", "tg"]:
        return False
    db_path = get_db_path(db_code)
    con = sqlite3.connect(db_path)
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
                    (uid, name, course, group, is_abitur))
    except sqlite3.IntegrityError:
        cur.execute("""UPDATE users
        SET name = ?, course = ?, groupa = ?, is_abitur = ?
        WHERE id == ?
        """, (name, course, group, is_abitur, uid))

    con.commit()
    con.close()
    return True


def get_user(db_code: str, uid: int) -> dict:
    """
        :param db_code: vk - БД юзеров ВК, tg - БД юзеров ТГ
        :param uid: Уникальный цифровой id юзера в мессенджере
        :return: Словарь со всей инфой о юзере. Словарь пустой, если юзер не авторизован (или неверно указан db_code)
    """

    user_dict = {}
    if db_code not in ["vk", "tg"]:
        return user_dict
    db_path = get_db_path(db_code)
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    udata = cur.execute("""SELECT * FROM users WHERE id == ?""", (uid,)).fetchone()
    if udata is None:
        return user_dict

    user_dict = {
        "id": udata[0],
        "name": udata[1],
        "course": udata[2],
        "group": udata[3],
        "is_abitur": bool(udata[4]),
    }

    if not user_dict["is_abitur"]:
        user_dict["course"] = cur.execute("""SELECT course FROM courses WHERE id == ?""",
                                          (user_dict["course"],)).fetchone()[0]
        user_dict["group"] = cur.execute("""SELECT groupa FROM groups WHERE id == ?""",
                                         (user_dict["group"],)).fetchone()[0]

    return user_dict
