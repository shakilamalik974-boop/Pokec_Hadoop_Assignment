import sys
from datetime import datetime

def mapper():
    for line in sys.stdin:
        cols = line.rstrip("\n").split("\t")
        if len(cols) < 7:
            continue

        try:
            user_id = cols[0]
            last_login = datetime.strptime(
                cols[5].split(".")[0], "%Y-%m-%d %H:%M:%S")
            registration = datetime.strptime(
                cols[6].split(".")[0], "%Y-%m-%d %H:%M:%S")

            days = (last_login - registration).days
            if days >= 0:
                print("%s\t%d" % (user_id, days))
        except (ValueError, IndexError):
            continue

def reducer():
    for line in sys.stdin:
        print(line.rstrip("\n"))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: script.py mapper|reducer")
    if sys.argv[1] == "mapper":
        mapper()
    elif sys.argv[1] == "reducer":
        reducer()
    else:
        sys.exit("Use mapper or reducer")
