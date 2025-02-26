import csv
import schedule

# Открытие TSV со всеми курсами (для следующего with)
with open("files/courses.tsv", "r", encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file, delimiter="\t")
    courses = [row["course"] for row in reader]

# TSV со всеми группами, разбитые по курсам (без id)
with open("files/groups.tsv", "w", encoding="utf-8", newline="") as csv_file:
    writer = csv.writer(csv_file, delimiter="\t")
    writer.writerow(["course", "group", "id"])
    for course in courses:
        groups = schedule.get_groups(course)
        for group in groups:
            writer.writerow([course, group, ""])
