#!/usr/bin/env python
# Python 2 compatible Hadoop Streaming
import sys
import os

def clean(value):
    value = value.strip()
    if value.lower() in ("", "null", "none", "unknown", "nan"):
        return None
    return value

def mapper():
    for line in sys.stdin:
        cols = line.rstrip("\n").split("\t")
        if len(cols) < 8:
            continue

        # Age: zero-based column 7
        age_text = clean(cols[7])
        try:
            age = float(age_text) if age_text is not None else None
        except ValueError:
            age = None

        if age is None or age <= 0 or age > 100:
            print("AGE_MISSING_OR_INVALID\tcount\t1")
        else:
            print("AGE_VALID_COUNT\tcount\t1")
            print("AGE_VALUE\t%.2f\t1" % age)

        # Completion percentage: zero-based column 2
        completion_text = clean(cols[2])
        try:
            completion = float(completion_text) if completion_text is not None else None
        except ValueError:
            completion = None

        if completion is None or completion < 0 or completion > 100:
            print("COMPLETION_MISSING_OR_INVALID\tcount\t1")
        else:
            print("COMPLETION_VALID_COUNT\tcount\t1")
            print("COMPLETION_VALUE\t%.2f\t1" % completion)

def reducer():
    counts = {}
    for line in sys.stdin:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 3:
            continue
        group, value, count_text = parts
        try:
            count = int(count_text)
        except ValueError:
            continue
        key = (group, value)
        counts[key] = counts.get(key, 0) + count

    for (group, value), count in sorted(counts.items()):
        print("%s\t%s\t%d" % (group, value, count))

if __name__ == "__main__":
    if os.environ.get("mapreduce_task_ismap", "").lower() == "true":
        mapper()
    else:
        reducer()