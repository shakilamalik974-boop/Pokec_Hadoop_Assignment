#!/usr/bin/env python
# Python 2 compatible Hadoop Streaming mapper/reducer

import sys
import os

def clean(value):
    value = value.strip()
    if value.lower() in ("", "null", "none", "unknown"):
        return None
    return value

def mapper():
    for line in sys.stdin:
        cols = line.rstrip("\n").split("\t")

        if len(cols) < 12:
            continue

        # Column 11: spoken languages
        languages = clean(cols[10])
        if languages:
            for item in languages.split(","):
                item = clean(item)
                if item:
                    print("LANGUAGE\t%s\t1" % item)

        # Column 12: hobbies
        hobbies = clean(cols[11])
        if hobbies:
            for item in hobbies.split(","):
                item = clean(item)
                if item:
                    print("HOBBY\t%s\t1" % item)

def reducer():
    counts = {}

    for line in sys.stdin:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 3:
            continue

        group, item, value = parts

        try:
            count = int(value)
        except ValueError:
            continue

        key = (group, item)
        counts[key] = counts.get(key, 0) + count

    for (group, item), count in sorted(counts.items()):
        print("%s\t%s\t%d" % (group, item, count))

if __name__ == "__main__":
    if os.environ.get("mapreduce_task_ismap", "").lower() == "true":
        mapper()
    else:
        reducer()