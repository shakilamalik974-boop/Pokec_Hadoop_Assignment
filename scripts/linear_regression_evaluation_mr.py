#!/usr/bin/env python
import sys

# Hadoop Streaming mapper/reducer.
# Usage: mapper | sort | reducer
# Input is read from stdin as raw Pokec TSV records.

def valid_record(line):
    cols = line.rstrip("\n").split("\t")
    try:
        uid = int(cols[1])
        y = float(cols[2])       # completion_percentage
        x = float(cols[7])       # age
        if x <= 0 or y < 0 or y > 100:
            return None
        return uid, x, y
    except (ValueError, IndexError):
        return None


def split_name(uid):
    # Stable split based on user ID; reproducible across runs.
    bucket = uid % 20
    if bucket <= 13:
        return "TRAIN"
    elif bucket <= 16:
        return "VALIDATION"
    return "TEST"


def mapper():
    for line_number, line in enumerate(sys.stdin):
        record = valid_record(line)
        if record is None:
            continue

        uid, x, y = record

        # Deterministic split based on input line position.
        bucket = line_number % 20
        if bucket < 14:
            split = "TRAIN"
        elif bucket < 17:
            split = "VALIDATION"
        else:
            split = "TEST"

        if split == "TRAIN":
            print("TRAIN\tN\t1")
            print("TRAIN\tSX\t%.8f" % x)
            print("TRAIN\tSY\t%.8f" % y)
            print("TRAIN\tSXX\t%.8f" % (x * x))
            print("TRAIN\tSXY\t%.8f" % (x * y))
        else:
            print("%s\tROW\t%.8f,%.8f" % (split, x, y))


def reducer():
    train_n = 0
    sx = sy = sxx = sxy = 0.0
    evaluation_rows = {"VALIDATION": [], "TEST": []}

    for line in sys.stdin:
        parts = line.rstrip("\n").split("\t", 2)
        if len(parts) != 3:
            continue

        group, key, value = parts

        if group == "TRAIN":
            try:
                v = float(value)
            except ValueError:
                continue

            if key == "N":
                train_n += int(v)
            elif key == "SX":
                sx += v
            elif key == "SY":
                sy += v
            elif key == "SXX":
                sxx += v
            elif key == "SXY":
                sxy += v

        elif group in ("VALIDATION", "TEST") and key == "ROW":
            try:
                x, y = [float(z) for z in value.split(",")]
                evaluation_rows[group].append((x, y))
            except ValueError:
                continue

    if train_n < 2:
        print("ERROR\tNot enough training records")
        return

    denominator = train_n * sxx - sx * sx
    if denominator == 0:
        print("ERROR\tCannot fit model: zero age variance")
        return

    slope = (train_n * sxy - sx * sy) / denominator
    intercept = (sy - slope * sx) / train_n

    print("TRAINING_RECORDS\t%d" % train_n)
    print("SLOPE\t%.6f" % slope)
    print("INTERCEPT\t%.6f" % intercept)

    for name in ("VALIDATION", "TEST"):
        rows = evaluation_rows[name]
        if not rows:
            print("%s\tNO_RECORDS" % name)
            continue

        actual = [y for x, y in rows]
        predicted = [slope * x + intercept for x, y in rows]
        mean_y = sum(actual) / float(len(actual))

        mae = sum(abs(y - p) for y, p in zip(actual, predicted)) / len(rows)
        mse = sum((y - p) ** 2 for y, p in zip(actual, predicted)) / len(rows)
        rmse = mse ** 0.5
        ss_total = sum((y - mean_y) ** 2 for y in actual)
        ss_res = sum((y - p) ** 2 for y, p in zip(actual, predicted))
        r2 = 1.0 - ss_res / ss_total if ss_total else 0.0

        print("%s_RECORDS\t%d" % (name, len(rows)))
        print("%s_MAE\t%.4f" % (name, mae))
        print("%s_RMSE\t%.4f" % (name, rmse))
        print("%s_R2\t%.4f" % (name, r2))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "reducer":
        reducer()
    else:
        mapper()