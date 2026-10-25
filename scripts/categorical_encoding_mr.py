#!/usr/bin/env python
# Python 2 compatible Hadoop Streaming
# Categorical frequency counting using MapReduce

import sys


def mapper():
    for line in sys.stdin:
        cols = line.rstrip('\n').split('\t')

        # Require at least the gender and region columns
        if len(cols) < 5:
            continue

        gender = cols[3].strip().lower()
        region = cols[4].strip().lower()

        # Emit gender category
        if gender and gender != 'null':
            print("GENDER_%s\t1" % gender)

        # Emit region category
        if region and region != 'null':
            print("REGION_%s\t1" % region)


def reducer():
    current_key = None
    total = 0

    for line in sys.stdin:
        parts = line.rstrip('\n').split('\t')

        if len(parts) != 2:
            continue

        key = parts[0]

        try:
            count = int(parts[1])
        except ValueError:
            continue

        if key == current_key:
            total += count
        else:
            if current_key is not None:
                print("%s\t%d" % (current_key, total))

            current_key = key
            total = count

    # Emit final category
    if current_key is not None:
        print("%s\t%d" % (current_key, total))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'reducer':
        reducer()
    else:
        mapper()