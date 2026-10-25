#!/usr/bin/env python
# Python 2 compatible Hadoop Streaming
import sys
import os

def mapper():
    for line in sys.stdin:
        cols = line.rstrip("\n").split("\t")
        if len(cols) < 8:
            continue

        # Age: column index 7
        try:
            age = float(cols[7].strip())
            if age > 0 and age <= 100:
                print("AGE\t%.2f" % age)
        except (ValueError, IndexError):
            pass

        # Completion percentage: column index 2
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
        data = sorted(values[group])
        n = len(data)
        if n == 0:
            continue

        # Linear interpolation percentile
        def percentile(sorted_data, p):
            pos = (len(sorted_data) - 1) * p
            low = int(pos)
            high = min(low + 1, len(sorted_data) - 1)
            fraction = pos - low
            return sorted_data[low] * (1 - fraction) + sorted_data[high] * fraction

        q1 = percentile(data, 0.25)
        q3 = percentile(data, 0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        print("%s\tCOUNT\t%d" % (group, n))
        print("%s\tQ1\t%.2f" % (group, q1))
        print("%s\tQ3\t%.2f" % (group, q3))
        print("%s\tIQR\t%.2f" % (group, iqr))
        print("%s\tLOWER_BOUND\t%.2f" % (group, lower))
        print("%s\tUPPER_BOUND\t%.2f" % (group, upper))

        for value in data:
            if value < lower or value > upper:
                print("%s\tOUTLIER\t%.2f" % (group, value))

if __name__ == "__main__":
    if os.environ.get("mapreduce_task_ismap", "").lower() == "true":
        mapper()
    else:
        reducer()