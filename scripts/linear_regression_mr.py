#!/usr/bin/env python
# Python 2 compatible Hadoop Streaming
# MapReduce Simple Linear Regression
# Feature: AGE
# Target: completion_percentage

import sys


def mapper():
    for line in sys.stdin:
        cols = line.rstrip('\n').split('\t')

        if len(cols) < 8:
            continue

        try:
            age = float(cols[7].strip())
            completion = float(cols[2].strip())

            if not (0 < age < 120 and 0 <= completion <= 100):
                continue

            # Statistics needed for linear regression
            print("N\t1")
            print("SUM_X\t%.8f" % age)
            print("SUM_Y\t%.8f" % completion)
            print("SUM_X2\t%.8f" % (age * age))
            print("SUM_XY\t%.8f" % (age * completion))

        except (ValueError, IndexError):
            continue


def reducer():
    stats = {
        "N": 0,
        "SUM_X": 0.0,
        "SUM_Y": 0.0,
        "SUM_X2": 0.0,
        "SUM_XY": 0.0
    }

    for line in sys.stdin:
        parts = line.rstrip('\n').split('\t')

        if len(parts) != 2:
            continue

        key, value = parts

        if key not in stats:
            continue

        try:
            stats[key] += float(value)
        except ValueError:
            continue

    n = stats["N"]
    sx = stats["SUM_X"]
    sy = stats["SUM_Y"]
    sx2 = stats["SUM_X2"]
    sxy = stats["SUM_XY"]

    denominator = n * sx2 - sx * sx

    if n > 1 and denominator != 0:
        slope = (n * sxy - sx * sy) / denominator
        intercept = (sy - slope * sx) / n

        print("TRAINING_RECORDS\t%d" % n)
        print("SLOPE\t%.6f" % slope)
        print("INTERCEPT\t%.6f" % intercept)
        print("MODEL\tcompletion_percentage = %.6f * age + %.6f"
              % (slope, intercept))
    else:
        print("ERROR\tInsufficient valid records")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'reducer':
        reducer()
    else:
        mapper()