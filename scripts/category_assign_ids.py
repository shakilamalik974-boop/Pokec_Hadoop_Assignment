#!/usr/bin/env python
# Python 2 compatible
# Assign IDs to sorted unique categories

import sys

current_feature = None
categories = []

def emit_ids(feature, values):
    for category_id, value in enumerate(sorted(set(values))):
        print("%s\t%s\t%d" % (feature, value, category_id))

for line in sys.stdin:
    parts = line.rstrip('\n').split('\t', 1)

    if len(parts) != 2:
        continue

    feature = parts[0].strip()
    category = parts[1].strip()

    if not feature or not category:
        continue

    if current_feature is None:
        current_feature = feature

    if feature != current_feature:
        emit_ids(current_feature, categories)
        current_feature = feature
        categories = []

    categories.append(category)

if current_feature is not None:
    emit_ids(current_feature, categories)