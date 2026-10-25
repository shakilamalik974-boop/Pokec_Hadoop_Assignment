#!/usr/bin/env python
# Python 2 compatible Hadoop Streaming

import sys


def mapper():
    for line in sys.stdin:
        cols = line.rstrip('\n').split('\t')
        if len(cols) < 5:
            continue

        gender = cols[3].strip().lower()
        region = cols[4].strip().lower()

        if gender and gender != 'null':
            print("GENDER\t%s" % gender)

        if region and region != 'null':
            print("REGION\t%s" % region)


def reducer():
    current_feature = None
    categories = []

    for line in sys.stdin:
        parts = line.rstrip('\n').split('\t', 1)
        if len(parts) != 2:
            continue

        feature, category = parts[0], parts[1].strip()
        if not category:
            continue

        if current_feature is None:
            current_feature = feature

        if feature != current_feature:
            for category_id, value in enumerate(sorted(set(categories))):
                print("%s\t%s\t%d" %
                      (current_feature, value, category_id))
            current_feature = feature
            categories = []

        categories.append(category)

    if current_feature is not None:
        for category_id, value in enumerate(sorted(set(categories))):
            print("%s\t%s\t%d" %
                  (current_feature, value, category_id))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'reducer':
        reducer()
    else:
        mapper()