#!/usr/bin/env python
# Python 2 compatible Hadoop Streaming mapper/reducer

import sys
import math
import os

def clean(value):
    value = value.strip()
    if value.lower() in ("", "null", "none", "unknown"):
        return None
    return value

def mapper():
    for line in sys.stdin:
        cols = line.rstrip("\n").split("\t")

        if len(cols) < 8:
            continue

        # Pokec profile columns (zero-based indices)
        completion = clean(cols[2])
        gender = clean(cols[3])
        region = clean(cols[4])
        age = clean(cols[7])

        # Categorical frequency counts
        if gender is not None:
            print("GENDER\t%s\t1" % gender)

        if region is not None:
            print("REGION\t%s\t1" % region)

        # Age statistics
        if age is not None:
            try:
                a = float(age)
                if a > 0 and a < 120:
                    print("AGE_STATS\tCOUNT\t1")
                    print("AGE_STATS\tSUM\t%.6f" % a)
                    print("AGE_STATS\tMIN\t%.6f" % a)
                    print("AGE_STATS\tMAX\t%.6f" % a)
            except:
                pass

        # Completion statistics and correlation inputs
        try:
            x = float(age)
            y = float(completion)

            if 0 < x < 120 and 0 <= y <= 100:
                print("CORR\tN\t1")
                print("CORR\tSX\t%.8f" % x)
                print("CORR\tSY\t%.8f" % y)
                print("CORR\tSXX\t%.8f" % (x*x))
                print("CORR\tSYY\t%.8f" % (y*y))
                print("CORR\tSXY\t%.8f" % (x*y))
        except:
            pass

def reducer():
    category_counts = {}
    stats = {}

    for line in sys.stdin:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 3:
            continue

        group, key, value = parts

        try:
            number = float(value)
        except:
            continue

        if group in ("GENDER", "REGION"):
            category = (group, key)
            category_counts[category] = category_counts.get(category, 0) + int(number)
        else:
            stats[(group, key)] = stats.get((group, key), 0.0) + number

    for (group, key), count in sorted(category_counts.items()):
        print("%s\t%s\t%d" % (group, key, count))

    age_count = stats.get(("AGE_STATS", "COUNT"), 0)
    age_sum = stats.get(("AGE_STATS", "SUM"), 0)
    if age_count:
        print("AGE_SUMMARY\tvalid_count\t%d" % age_count)
        print("AGE_SUMMARY\tmean_age\t%.2f" % (age_sum / age_count))

    n = stats.get(("CORR", "N"), 0)
    if n > 1:
        sx = stats.get(("CORR", "SX"), 0)
        sy = stats.get(("CORR", "SY"), 0)
        sxx = stats.get(("CORR", "SXX"), 0)
        syy = stats.get(("CORR", "SYY"), 0)
        sxy = stats.get(("CORR", "SXY"), 0)

        numerator = n * sxy - sx * sy
        denominator = math.sqrt(
            max(0, n*sxx - sx*sx) * max(0, n*syy - sy*sy)
        )

        if denominator > 0:
            correlation = numerator / denominator
            print("CORRELATION\tage_vs_completion\t%.4f" % correlation)
        else:
            print("CORRELATION\tage_vs_completion\tundefined")

if __name__ == "__main__":
    if os.environ.get("mapreduce_task_ismap", "").lower() == "true":
        mapper()
    else:
        reducer()