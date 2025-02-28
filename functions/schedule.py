"""
Функции, связанные с расписаниями.

Расписание можно получить:
1. По группе
2. По преподавателю

Расписание можно получить на сегодня, завтра, послезавтра или всю неделю.
Студент может получить быстрое расписание по своей группе, не вводя ее каждый раз.
"""

import csv
import datetime as dt

import pandas
import requests

with open("functions/files/courses.tsv", "r", encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file, delimiter="\t")
    course_urls = dict()
    for row in reader:
        course_urls[row["course"]] = row["id"]

groups_urls = pandas.read_csv("functions/files/groups.tsv", delimiter="\t")

teachers_urls = pandas.read_csv("files/teachers.tsv", delimiter="\t")


def get_groups(course: str) -> list:
    """
    :param course: Курс (напр. Бакалавриат, 1 курс)
    :return: Список групп на курсе
    """

    url = f"https://schedule.sfedu.ru/APIv1/group/forGrade/{course_urls[course]}"
    response = requests.get(url=url).json()
    groups = list()
    for group in response:
        groups.append(f"{group['name']}, {group['num']} группа")
    return groups


def get_teachers(pre_teacher: str) -> list:
    """
    :param pre_teacher: строка от пользователя
    :return: список учителей, ФИО которых включает строку от пользователя
    """

    pre_teacher = pre_teacher.lower()
    teachers = teachers_urls[teachers_urls.teacher.str.contains(pre_teacher, case=False, na=False)]
    teachers = list(teachers.teacher.tolist())
    teachers.sort(key=lambda x: x.lower()[0] != pre_teacher[0])
    return teachers


def schedule_parser(response: dict, period: str) -> dict:
    # Вспомогательная функция, не для обычного использования
    lessons = pandas.DataFrame(response["lessons"])
    lessons["weekday"] = lessons["timeslot"].transform(lambda x: x[1])
    lessons["start_time"] = lessons["timeslot"].transform(lambda x: x[3:8])
    lessons["end_time"] = lessons["timeslot"].transform(lambda x: x[12:17])
    lessons = lessons.sort_values(by=["weekday", "start_time"])

    curricula = pandas.DataFrame(response["curricula"])

    weekday = dt.datetime.today().weekday()
    if period == "today":
        pass
    elif period == "tomorrow":
        weekday += 1
    elif period == "atomorrow":
        weekday += 2
    elif period == "week":
        weekday = None
    if weekday:
        if weekday > 6:
            weekday -= 7
        lessons = lessons[lessons.weekday == str(weekday)]

    schedule = dict()
    for index, row in lessons.iterrows():
        curric = curricula[curricula.lessonid == row["id"]]
        if row["weekday"] not in schedule.keys():
            schedule[row["weekday"]] = list()
        for indx, rowc in curric.iterrows():
            schedule[row["weekday"]].append({
                "title": rowc["subjectname"],
                "teacher": rowc["teachername"],
                "room": rowc["roomname"],
                "info": row["info"],
                "start_time": row["start_time"],
                "end_time": row["end_time"],
            })

    return schedule


def get_schedule(course: str, group: str, period: str = "week") -> dict:
    """
    :param course: Курс полностью (напр: Бакалавриат, 1 курс)
    :param group: Группа полностью (напр: ПМИ, 1 группа)
    :param period: За какой период нужно расписание (today - сегодня, tomorrow - завтра, atomorrow - послезавтра, week - неделя)
    :return:
    """

    group_url = groups_urls[groups_urls.course == course][groups_urls.group == group].get("id").iat[0]
    url = f"https://schedule.sfedu.ru/APIv1/schedule/group/{group_url}"
    response = requests.get(url=url).json()
    schedule = schedule_parser(response, period)
    return schedule


def get_teacher_schedule(teacher: str, period: str = "week") -> dict:
    """
    :param teacher: Точное ФИО преподавателя в системе
    :param period: За какой период нужно расписание (today - сегодня, tomorrow - завтра, atomorrow - послезавтра, week - неделя)
    :return:
    """

    teacher_url = teachers_urls[teachers_urls.teacher == teacher].get("id").iat[0]
    url = f"https://schedule.sfedu.ru/APIv1/schedule/teacher/{teacher_url}"
    response = requests.get(url=url).json()
    schedule = schedule_parser(response, period)
    return schedule
