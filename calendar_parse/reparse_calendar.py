import os
import requests

FLAG: bool = False
TEACHER: str = ''
studentid = 1091  # for Hannah Ivy

new_timetable: str = 'fixed_timetable.ics'
unparsed_timetable: str = 'timetable.ics'
if os.path.isfile(new_timetable):
    os.remove(new_timetable)
if not os.path.isfile(unparsed_timetable):
    url = f"https://web1.normanhurb-h.schools.nsw.edu.au/timetables/timetable?student={studentid}&action=export"
    response = requests.get(url)
    with open(unparsed_timetable, 'wb') as file:
        file.write(response.content)


file = open(unparsed_timetable, 'r').readlines()
new_file = open(new_timetable, 'w')


for line in file:
    if FLAG:
        line: str = line.strip()
        FLAG = False
        line = line.replace('SUMMARY: ', '')
        subject = line.split(": ")[1]
        new_file.write(f'SUMMARY:{subject.title()} with {TEACHER.title()}\n')
    elif line.startswith('DESCRIPTION:'):
        line = line.replace('DESCRIPTION:', '')
        line: str = line.strip()
        FLAG = True
        arr: list = line.split('\\n')
        TEACHER = arr[0].split(':')[1].strip()
        period: str = arr[1]
        new_file.write(f'DESCRIPTION:{period.title()}\n')
    elif line.startswith("LOCATION:"):
        line = line.replace('LOCATION:', '')
        line: str = line.strip()
        room = line.split(': ')[1]
        new_file.write(f'LOCATION:Room {room.upper()}\n')
    else:
        new_file.write(line)