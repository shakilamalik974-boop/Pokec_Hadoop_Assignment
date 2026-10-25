import sys

mode = sys.argv[1]

if mode == "mapper":
    for line in sys.stdin:
        fields = line.rstrip("\r\n").split("\t")
        if len(fields) != 60:
            continue
        try:
            value = float(fields[2])
            if value >= 0:
                print("completion\t{0}".format(value))
        except (ValueError, IndexError):
            pass

elif mode == "reducer":
    count = 0
    total = 0.0
    minimum = float("inf")
    maximum = float("-inf")

    for line in sys.stdin:
        parts = line.rstrip("\r\n").split("\t")
        if len(parts) != 2:
            continue
        try:
            value = float(parts[1])
        except ValueError:
            continue

        count += 1
        total += value
        minimum = min(minimum, value)
        maximum = max(maximum, value)

    if count:
        print("Records analyzed: {0}".format(count))
        print("Minimum completion: {0:.2f}".format(minimum))
        print("Maximum completion: {0:.2f}".format(maximum))
        print("Average completion: {0:.2f}".format(total / count))
