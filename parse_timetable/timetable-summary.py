import requests
from bs4 import BeautifulSoup
from colorama import init as colourinit
from colorama import Fore
from colorama import Style

colourinit()

STUDENTS: dict = {}
HEADER: list = []


def get_subjects_from_student_id(studentid: int) -> tuple:
    ret: dict = {}
    url: str = f"https://web1.normanhurb-h.schools.nsw.edu.au/timetables/timetable?student={studentid}&show=cyclical"
    request: requests.models.Response = requests.get(url)
    html: str = request.text
    parsed: BeautifulSoup = BeautifulSoup(html, 'html.parser')
    classes: list = parsed.find_all("div", class_="timetable-class")
    full_name: str = parsed.title.string.split(' -')[0]
    subjects = []
    for cls in classes:
        arr: list = cls.text.strip().replace("\n", "").split('(')
        subj_name: str = arr[0].strip()
        remains: str = f"({arr[1].strip()}"
        r_arr: list = remains.split()
        class_id = r_arr[0].replace('(', '').replace(')', '')
        ret[subj_name] = class_id
        if subj_name not in subjects:
            subjects.append(subj_name)
    return ret, full_name, subjects


if __name__ == "__main__":
    try:
        students_moved = open('broken_students.py', 'w')
        file = open('out.csv', 'w')
    except PermissionError:
        print(f"{Fore.RED}You appear to have either broken_students.py and/or out.csv open right now.{Style.RESET_ALL}")
        print(f"{Fore.RED}Please exit these for the program to function to correctly.{Style.RESET_ALL}")
        exit(1)
        students_moved, file = None, None
    students_moved.write('students_to_remove: list = [')
    to_check = [num for num in range(1064, 1187)]
    later_students = [1191, 1335, 1339, 1334, 1361, 1363, 1364]
    students_to_remove: list = [1065, 1067, 1071, 1086, 1089, 1094, 1108, 1110, 1115, 1120, 1130, 1133, 1136, 1138,
                                1143, 1145, 1151, 1160, 1161, 1180, 1182, 1184, 1335]
    for student in later_students:
        to_check.append(student)
    for student in students_to_remove:
        to_check.remove(student)
    # to_check = [1091, 1093]
    for student in to_check:
        classes_dict, name, new_subjects = get_subjects_from_student_id(student)
        if len(classes_dict) < 1:
            students_moved.write(f'{student}, ')
            print(f"{Fore.RED}!  {student} - {name} no longer exists.{Style.RESET_ALL}")
        else:
            for subject in new_subjects:
                if subject not in HEADER:
                    HEADER.append(subject)
            STUDENTS[name] = classes_dict
            print(f"{Fore.GREEN}:) {student} - {name} completed successfully.{Style.RESET_ALL}")
    file.write(f'Last name, First name,{",".join(HEADER)}\n')
    for student_name, student_classes in STUDENTS.items():
        out: str = f"{student_name},"
        student_subjects: list = []
        for stud_subj in student_classes:
            student_subjects.append(stud_subj)
        for subject in HEADER:
            if subject in student_subjects:
                out += f"{student_classes[subject]},"
            else:
                out += ','
        file.write(f"{out}\n")
    students_moved.write(']\n')
    exit(0)

