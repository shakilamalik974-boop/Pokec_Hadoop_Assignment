#!/usr/bin/env python
# Python 2 compatible Hadoop Streaming
import sys
import os

def mapper():
    for line in sys.stdin:
        cols = line.rstrip("\n").split("\t")
        if len(cols) < 8:
            continue

        try:
            age = float(cols[7].strip())
            if 0 < age <= 100:
                print("AGE\t%.2f" % age)
        except (ValueError, IndexError):
            pass

        try:
            completion = float(cols[2].strip())
            if 0 <= completion <= 100:
                print("COMPLETION\t%.2f" % completion)
        except (ValueError, IndexError):
            pass

def reducer():
    values = {"AGE": [], "COMPLETION": []}

    for line in sys.stdin:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 2:
            continue
        group, value = parts
        if group not in values:
            continue
        try:
            values[group].append(float(value))
        except ValueError:
            pass

    for group in ("AGE", "COMPLETION"):
        data = values[group]
        if not data:
            continue

        min_value = min(data)
        max_value = max(data)
        print("%s\tMIN\t%.2f" % (group, min_value))
        print("%s\tMAX\t%.2f" % (group, max_value))

        for value in sorted(data):
            if max_value == min_value:
                normalized = 0.0
            else:
                normalized = (value - min_value) / (max_value - min_value)
            print("%s\tORIGINAL_%.2f\tNORMALIZED_%.4f" %
                  (group, value, normalized))

if __name__ == "__main__":
    if os.environ.get("mapreduce_task_ismap", "").lower() == "true":
        mapper()
    else:
        reducer()