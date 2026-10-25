import sys
from datetime import datetime

mode = sys.argv[1]


def parse_date(value):
    try:
        value = value.strip()
        if value.endswith(".0"):
            value = value[:-2]
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None


if mode == "mapper":
    for line in sys.stdin:
        fields = line.rstrip("\r\n").split("\t")

        if len(fields) != 60:
            continue

        # Completion percentage: column 3 (index 2)
        try:
            completion = float(fields[2])
            if 0 <= completion <= 100:
                print("completion\t{0}".format(completion))
        except (ValueError, IndexError):
            pass

        # last_login: column 6 (index 5)
        # registration: column 7 (index 6)
        last_login = parse_date(fields[5])
        registration = parse_date(fields[6])

        if last_login and registration:
            days = (last_login - registration).total_seconds() / 86400.0

            if days >= 0:
                print("registration_days\t{0}".format(days))


elif mode == "reducer":
    stats = {}

    for line in sys.stdin:
        parts = line.rstrip("\r\n").split("\t")

        if len(parts) != 2:
            continue

        key = parts[0]

        try:
            value = float(parts[1])
        except ValueError:
            continue

        if key not in stats:
            stats[key] = {
                "count": 0,
                "total": 0.0,
                "minimum": float("inf"),
                "maximum": float("-inf")
            }

        stats[key]["count"] += 1
        stats[key]["total"] += value
        stats[key]["minimum"] = min(stats[key]["minimum"], value)
        stats[key]["maximum"] = max(stats[key]["maximum"], value)

    if "completion" in stats:
        s = stats["completion"]
        print("Completion records analyzed: {0}".format(s["count"]))
        print("Minimum completion: {0:.2f}".format(s["minimum"]))
        print("Maximum completion: {0:.2f}".format(s["maximum"]))
        print("Average completion: {0:.2f}".format(
            s["total"] / s["count"]))

    if "registration_days" in stats:
        s = stats["registration_days"]
        print("Valid registration intervals: {0}".format(s["count"]))
        print("Average days since registration: {0:.2f}".format(
            s["total"] / s["count"]))