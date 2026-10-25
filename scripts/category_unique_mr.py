#!/usr/bin/env python
# Python 2 compatible Hadoop Streaming
# Stage 1: Emit categorical values for unique-category extraction

import sys

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