import os                                # Check if timetable exists already
import sys                               # Get user arguments
import requests                          # To download the file
from colorama import init as colourinit  # To make colours work on windows
from colorama import Fore                # Change colour of text
from colorama import Style               # Allows me to reset colour
import dateutil.parser                   # Parses time
from dateutil.tz import tzutc            # Converts time back

colourinit()

# Days

STANDARD: dict  = {
    "day"  : None,
    "start": {
            "p1": {
                "hour": 8,
                "minute": 40 
            },
            "p2": {
                "hour": 9,
                "minute": 44
            },
            "p3": {
                "hour": 11,
                "minute": 8
            },
            "p4": {
                "hour": 12,
                "minute": 12
            },
            "p5": {
                "hour": 13,
                "minute": 56
            },
    },
    "end": {
            "p1": {
            "hour": 9,
            "minute": 44 
        },
        "p2": {
            "hour": 10,
            "minute": 48
        },
        "p3": {
            "hour": 12,
            "minute": 12
        },
        "p4": {
            "hour": 13,
            "minute": 16
        },
        "p5": {
            "hour": 15,
            "minute": 00
        },
    }
}

WEDNESDAY: dict = {
    "day": 3,
    "start": {
        "p1": {
            "hour": 8,
            "minute": 40 
        },
        "p2": {
            "hour": 9,
            "minute": 36
        },
        "p3": {
            "hour": 10,
            "minute": 52
        },
    },
    "end": {
        "p1": {
            "hour": 9,
            "minute": 36 
        },
        "p2": {
            "hour": 10,
            "minute": 32
        },
        "p3": {
            "hour": 11,
            "minute": 48
        },
    },
}
THURSDAY: dict = {
    "day": 4,
    "start": {
        "p1": {
            "hour": 8,
            "minute": 40 
        },
        "p2": {
            "hour": 9,
            "minute": 41
        },
        "p3": {
            "hour": 11,
            "minute": 17
        },
        "p4": {
            "hour": 12,
            "minute": 18
        },
        "p5": {
            "hour": 13,
            "minute": 59
        },
    },
    "end": {
        "p1": {
            "hour": 9,
            "minute": 41 
        },
        "p2": {
            "hour": 10,
            "minute": 42
        },
        "p3": {
            "hour": 12,
            "minute": 18
        },
        "p4": {
            "hour": 13,
            "minute": 19
        },
        "p5": {
            "hour": 15,
            "minute": 0
        },
    }
}

FLAG: bool = False
# Flag for if there is an event, so we can parse the next line

TEACHER: str = ''
# The teacher that we parse, as we put it later.

NUMBER: int = 0
# The number of events we have parsed, basically to flex

ENDPOINT: str = "https://web1.normanhurb-h.schools.nsw.edu.au/"

SUBJECTS, TEACHERS = {}, {}

print(f"{Fore.CYAN}Set up variables. {Style.RESET_ALL}")

# Delete the existing timetable
fixed_timetable: str = 'fixed_timetable.ics'
unparsed_timetable: str = 'timetable.ics'

if os.path.isfile(fixed_timetable):
    os.remove(fixed_timetable)
if os.path.isfile(unparsed_timetable):
    os.remove(unparsed_timetable)

print(f"{Fore.CYAN}Deleted any pre-existing file(s).{Style.RESET_ALL}")


# Set student ID
if len(sys.argv) == 2:  # If we get a student id
    studentid = int(sys.argv[1])  # Declare it
else:
    print(f"{Fore.CYAN}You can get your student id from the timetable site.")
    print(f"https://web1.normanhurb-h.schools.nsw.edu.au/timetables/")
    print(f"For instance, if when you click your name, your url looks like this:")
    print(f"https://web1.normanhurb-h.schools.nsw.edu.au/timetables/timetable?student={Fore.RED}1091{Fore.CYAN}")
    print(f"Then you enter in '{Fore.RED}1091{Fore.CYAN}'")
    print(f"Student ID{Style.RESET_ALL}: ",end='')
    studentid = int(input())  


print(f"{Fore.CYAN}Downloading unparsed timetable for {studentid}.{Style.RESET_ALL}")

# Download and write the corresponding timetable
url = f"{ENDPOINT}timetables/timetable?student={studentid}&action=export"
response = requests.get(url)

print(f"{Fore.CYAN}Downloaded unparsed timetable for {studentid}.{Style.RESET_ALL}")

# Write to the unparsed file
with open(unparsed_timetable, 'wb') as unparsed_file:
    unparsed_file.write(response.content)
print(f"{Fore.CYAN}Stored it as {unparsed_timetable}.{Style.RESET_ALL}")

# Set the files
unparsed_file = open(unparsed_timetable, 'r').readlines()
new_file = open(fixed_timetable, 'w')

# For each line in the calendar
r"""
Sidenote: Here's what a file looks like:
```ics
BEGIN:VEVENT
DTSTART;VALUE=DATE-TIME:20190131T000800Z
DTSTAMP;VALUE=DATE-TIME:20190119T010941Z
DTEND;VALUE=DATE-TIME:20190131T011200Z
UID:2fd6d8dc247722f904a09e93641c42b074156b24@sentral.local
DESCRIPTION:Teacher:  Angela Ellen\nPeriod: P3
SUMMARY:11_11GEO: YEAR 12  GEOGRAPHY
LOCATION:Room: 14
END:VEVENT
```
"""

def clean_line(line: str, title: str) -> str:
    """
    Removes EOL from lines and strips the title out.
    """
    return line.replace(title, "").strip()

for line in unparsed_file:
    oline = line[:]
    # If the previous line was a description (This line will be a title)
    # (Because Sentral puts titles after description)
    if line.startswith("DTSTART"):
        line = clean_line(line, "DTSTART;VALUE=DATE-TIME:")
        time = dateutil.parser.parse(line).astimezone()
        weekday = time.isoweekday()
        if weekday == WEDNESDAY["day"] or weekday == THURSDAY["day"]:
            pd: str
            for period, times in STANDARD["start"].items():
                if time.hour == times["hour"] and time.minute == times["minute"]:
                    pd = period
                    break
            else:
                pd = -1
                # its period 0 or 6
                    
            if pd != -1:
                if weekday == WEDNESDAY["day"]: 
                    if pd in WEDNESDAY["start"]:
                        h = WEDNESDAY["start"][pd]["hour"]
                        m = WEDNESDAY["start"][pd]["minute"]
                        time = time.replace(hour=h, minute=m)
                        time = time.astimezone(tzutc())
                        new_file.write(f'DTSTART;VALUE=DATE-TIME:{time.strftime("%Y%m%dT%H%M%SZ")}\n')
                elif weekday == THURSDAY["day"]: 
                    if pd in THURSDAY["start"]:
                        h = THURSDAY["start"][pd]["hour"]
                        m = THURSDAY["start"][pd]["minute"]
                        time = time.replace(hour=h, minute=m)
                        time = time.astimezone(tzutc())
                        new_file.write(f'DTSTART;VALUE=DATE-TIME:{time.strftime("%Y%m%dT%H%M%SZ")}\n')
            else: 
                new_file.write(oline)
        else:
            new_file.write(oline)

    elif line.startswith("DTEND"):
        line = clean_line(line, "DTEND;VALUE=DATE-TIME:")
        time = dateutil.parser.parse(line).astimezone()
        weekday = time.isoweekday()
        if weekday == WEDNESDAY["day"] or weekday == THURSDAY["day"]:
            pd: str
            for period, times in STANDARD["end"].items():
                if time.hour == times["hour"] and time.minute == times["minute"]:
                    pd = period
                    break
            else:
                pd = -1
            if pd != -1:
                if weekday == WEDNESDAY["day"]: 
                    if pd in WEDNESDAY["end"]:
                        h = WEDNESDAY["end"][pd]["hour"]
                        m = WEDNESDAY["end"][pd]["minute"]
                        time = time.replace(hour=h, minute=m)
                        time = time.astimezone(tzutc())
                        new_file.write(f'DTEND;VALUE=DATE-TIME:{time.strftime("%Y%m%dT%H%M%SZ")}\n')
                elif weekday == THURSDAY["day"]: 
                    if pd in THURSDAY["end"]:
                        h = THURSDAY["end"][pd]["hour"]
                        m = THURSDAY["end"][pd]["minute"]
                        time = time.replace(hour=h, minute=m)
                        time = time.astimezone(tzutc())
                        new_file.write(f'DTEND;VALUE=DATE-TIME:{time.strftime("%Y%m%dT%H%M%SZ")}\n')
            else:
                new_file.write(oline)
        else:
            new_file.write(oline)

    elif FLAG:
        # Remove preamble for parsing
        line = clean_line(line , 'SUMMARY: ')

        # We dealt with that flag
        FLAG = False

        # Get the subject, given that it is after the first colon ("Teacher:")
        # And remove the "YEAR 12" for accelerated subjects
        subject = line.split(": ")[1].replace("YEAR 12", "").strip().title()

        # Adds the subject to a dict
        if subject in SUBJECTS:
            SUBJECTS[subject] += 1
        else:
            SUBJECTS[subject] = 0
        # And write it in the file
        new_file.write(f'SUMMARY:{subject} with {TEACHER}\n')

        # Print it to the user in colours
        print(f"Processed "
              f"{Fore.CYAN}{subject}{Style.RESET_ALL} with "
              f"{Fore.CYAN}{TEACHER}{Style.RESET_ALL}")
        
        # Iterate the number of events we parsed.
        NUMBER += 1
    # If the line is a description
    elif line.startswith('DESCRIPTION:'):
        # Remove preamble for parsing
        line = clean_line(line , 'DESCRIPTION:')

        # Prep the flag, as the next line will be a title
        FLAG = True

        # Create an array of the line 
        # An escaped newline seperates the teacher and the period
        # TEACHER is a global because we move it in to the title
        arr: list = line.split('\\n')
        TEACHER = arr[0].strip("Teacher: ").title()

        # Add the teacher to a dict
        if TEACHER in TEACHERS:
            TEACHERS[TEACHER] += 1
        else:
            TEACHERS[TEACHER] = 0

        PERIOD = arr[0].strip("Period: ")

        # Write only the period in the description now
        new_file.write(f'DESCRIPTION:{PERIOD.title()}\n')
    
    # If it's the room
    elif line.startswith("LOCATION:"):
        # Remove the preamble
        room: str = clean_line(line , 'LOCATION:Room: ')
        # Print it out
        new_file.write(f'LOCATION:Room {room.upper()}\n')
    else:
        new_file.write(line)

print(f"{Fore.CYAN}Stored the new file as \"{fixed_timetable}\".{Style.RESET_ALL}")

print(f"{Fore.CYAN}Processed "
      f"{Fore.RED}{NUMBER}{Fore.CYAN} events!{Style.RESET_ALL}")

print(f"{Fore.YELLOW}Here are the subjects you have:{Style.RESET_ALL}")
for subject, times in SUBJECTS.items():
    print("You have "
    f"{Fore.CYAN}{subject} {Fore.RED}{times}{Style.RESET_ALL} times a fortnight.")

print(f"{Fore.YELLOW}Here are the teachers you have:{Style.RESET_ALL}")
for teacher, times in TEACHERS.items():
    print("You have "
          f"{Fore.CYAN}{teacher} {Fore.RED}{times}{Style.RESET_ALL} times a fortnight.")
print(f"=============================================")
print(f"{Fore.BLUE} To download your new calendar, open "
      f"{Fore.RED}fixed_timetable.ics{Fore.BLUE} from the "
      f"sidebar on the left, and press {Fore.RED}Control "
      f"{Fore.BLUE} or {Fore.RED}Command{Fore.BLUE} + {Fore.RED}A "
      f"{Fore.BLUE} and then press {Fore.RED}Control{Fore.BLUE} "
      f"or {Fore.RED}Command{Fore.BLUE} + {Fore.RED}C{Fore.BLUE}."
      "\n"
      f"Then, open {Fore.RED}Notepad or similar{Fore.BLUE} and save "
      f"it to somewhere you will remember."
      "\n"
      f"Then, open Google Calendar, and press the three dots next to "
      f"\"{Fore.RED}My calendars\"{Fore.BLUE}, and then press "
      f"\"{Fore.RED}New calendar\"{Fore.BLUE}. Name it what you want, "
      f"and then press \"{Fore.RED}Create calendar\"{Fore.BLUE}. Next, "
      f"press \"{Fore.RED}Import & export\"{Fore.BLUE} from the left sidebar. "
      f"Select the file you saved earlier, and change "
      f"\"{Fore.RED}Add to calendar\"{Fore.BLUE} to the one we just made."
      f"Now, just press \"{Fore.RED}Import\"{Fore.BLUE}, and you're done!"
)