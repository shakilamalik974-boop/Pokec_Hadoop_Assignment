#!/usr/bin/env python
import sys
import random
import math

# Mapper: extract features and assign reproducible data splits
def mapper():
    for line_number, line in enumerate(sys.stdin):
        cols = line.rstrip("\n").split("\t")

        try:
            completion = float(cols[2])
            gender = float(cols[3])
            age = float(cols[7])

            # Skip missing or invalid values
            if age <= 0 or completion < 0 or completion > 100:
                continue

            # Deterministic split using original input line number
            bucket = line_number % 10

            if bucket < 7:
                split = "TRAIN"
            elif bucket < 9:
                split = "VALIDATION"
            else:
                split = "TEST"

            print("%s\t%.4f,%.4f,%.4f" %
                  (split, age, gender, completion))

        except (ValueError, IndexError):
            continue


# Calculate mean completion percentage
def mean(rows):
    if not rows:
        return 0.0
    return sum(row[2] for row in rows) / float(len(rows))


# Train a decision stump on one selected feature
def train_stump(rows, feature_index):
    values = sorted(row[feature_index] for row in rows)

    if len(values) < 2:
        threshold = values[0] if values else 0.0
    else:
        threshold = (values[len(values) // 2 - 1] +
                     values[len(values) // 2]) / 2.0

    left = [r for r in rows if r[feature_index] <= threshold]
    right = [r for r in rows if r[feature_index] > threshold]

    return {
        "feature": feature_index,
        "threshold": threshold,
        "left_mean": mean(left),
        "right_mean": mean(right)
    }


# Predict using a trained stump
def stump_predict(stump, age, gender):
    features = [age, gender]
    value = features[stump["feature"]]

    if value <= stump["threshold"]:
        return stump["left_mean"]
    return stump["right_mean"]


# Reducer: train and evaluate a small randomized stump ensemble
def reducer():
    data = {
        "TRAIN": [],
        "VALIDATION": [],
        "TEST": []
    }

    for line in sys.stdin:
        parts = line.rstrip("\n").split("\t", 1)

        if len(parts) != 2 or parts[0] not in data:
            continue

        try:
            age, gender, completion = [
                float(v) for v in parts[1].split(",")
            ]
            data[parts[0]].append((age, gender, completion))
        except ValueError:
            continue

    train = data["TRAIN"]

    print("MODEL\tSimplified Randomized Stump Ensemble")
    print("METHOD\tBootstrap sampling and random feature selection")
    print("TRAINING_RECORDS\t%d" % len(train))
    print("VALIDATION_RECORDS\t%d" % len(data["VALIDATION"]))
    print("TEST_RECORDS\t%d" % len(data["TEST"]))

    if len(train) < 4:
        print("ERROR\tInsufficient training records")
        return

    # Fixed seed makes the experiment reproducible
    random.seed(42)

    number_of_trees = 10
    ensemble = []

    # Train multiple stumps using bootstrap samples
    for tree_number in range(number_of_trees):
        bootstrap = [
            random.choice(train) for _ in range(len(train))
        ]

        # Randomly select one feature for each stump
        feature_index = random.choice([0, 1])

        stump = train_stump(bootstrap, feature_index)
        ensemble.append(stump)

    # Average predictions from all stumps
    def predict(age, gender):
        predictions = [
            stump_predict(stump, age, gender)
            for stump in ensemble
        ]
        return sum(predictions) / float(len(predictions))

    print("ENSEMBLE_SIZE\t%d" % len(ensemble))

    # Evaluate validation and test sets separately
    for split_name in ("VALIDATION", "TEST"):
        rows = data[split_name]

        if not rows:
            print("%s\tNO_RECORDS" % split_name)
            continue

        errors = [
            row[2] - predict(row[0], row[1])
            for row in rows
        ]

        mae = sum(abs(error) for error in errors) / float(len(errors))
        rmse = math.sqrt(
            sum(error * error for error in errors) / float(len(errors))
        )

        actual = [row[2] for row in rows]
        actual_mean = mean(rows)
        ss_total = sum((y - actual_mean) ** 2 for y in actual)
        ss_res = sum(error * error for error in errors)

        r2 = 1.0 - ss_res / ss_total if ss_total > 0 else 0.0

        print("%s_MAE\t%.4f" % (split_name, mae))
        print("%s_RMSE\t%.4f" % (split_name, rmse))
        print("%s_R2\t%.4f" % (split_name, r2))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "reducer":
        reducer()
    else:
        mapper()