"""
Функции, связанные с расписаниями.

Расписание можно получить:
1. По группе
2. По преподавателю
3. По аудитории

Расписание можно получить на сегодня, завтра, послезавтра или всю неделю.
Студент может получить быстрое расписание по своей группе, не вводя ее каждый раз.
"""

import requests
import csv

with open("files/courses.tsv", "r", encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file, delimiter="\t")
    course_urls = dict()
    for row in reader:
        course_urls[row["course"]] = row["id"]


# Получить список групп по названию курса
def get_groups(course: str) -> list:
    url = f"https://schedule.sfedu.ru/APIv1/group/forGrade/{course_urls[course]}"
    response = requests.get(url=url).json()
    groups = list()
    for group in response:
        groups.append(f"{group['name']}, {group['num']} группа")
    return groups

