import csv
import sys

def mapper():
    for line in sys.stdin:
        fields = line.rstrip("\r\n").split("\t")

        if len(fields) != 60:
            continue

        try:
            # Column 3: completion_percentage (index 2)
            completion = float(fields[2])

            if completion >= 0:
                print(f"completion\t{completion}")
        except ValueError:
            continue

def reducer():
    count = 0
    total = 0.0
    minimum = float("inf")
    maximum = float("-inf")

    for line in sys.stdin:
        try:
            key, value = line.rstrip("\n").split("\t")
            value = float(value)
        except ValueError:
            continue

        count += 1
        total += value
        minimum = min(minimum, value)
        maximum = max(maximum, value)

    if count:
        print(f"Records analyzed: {count}")
        print(f"Minimum completion: {minimum:.2f}")
        print(f"Maximum completion: {maximum:.2f}")
        print(f"Average completion: {total / count:.2f}")

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("mapper", "reducer"):
        raise SystemExit("Usage: python completion_analysis.py mapper|reducer")

    if sys.argv[1] == "mapper":
        mapper()
    else:
        reducer()