import gzip
import math
import random

INPUT_FILE = r"E:\Pokec_Hadoop_Assignment\data\pokec_100.txt"
RANDOM_SEED = 42


def load_data():
    records = []

    with open(INPUT_FILE, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            cols = line.rstrip("\n").split("\t")

            try:
                user_id = int(cols[1])
                completion = float(cols[2])
                age = float(cols[7])

                if age > 0 and 0 <= completion <= 100:
                    records.append((user_id, age, completion))
            except (ValueError, IndexError):
                continue

    return records


def predict(x, slope, intercept):
    return slope * x + intercept


def fit_linear_regression(records):
    n = len(records)
    mean_x = sum(r[1] for r in records) / n
    mean_y = sum(r[2] for r in records) / n

    denominator = sum((r[1] - mean_x) ** 2 for r in records)

    if denominator == 0:
        raise ValueError("Training ages have no variation.")

    slope = sum(
        (r[1] - mean_x) * (r[2] - mean_y)
        for r in records
    ) / denominator

    intercept = mean_y - slope * mean_x
    return slope, intercept


def evaluate(records, slope, intercept):
    actual = [r[2] for r in records]
    predicted = [predict(r[1], slope, intercept) for r in records]

    mae = sum(abs(a - p) for a, p in zip(actual, predicted)) / len(actual)

    rmse = math.sqrt(
        sum((a - p) ** 2 for a, p in zip(actual, predicted)) / len(actual)
    )

    mean_y = sum(actual) / len(actual)
    ss_total = sum((a - mean_y) ** 2 for a in actual)
    ss_residual = sum((a - p) ** 2 for a, p in zip(actual, predicted))

    r2 = 1 - ss_residual / ss_total if ss_total else 0

    return mae, rmse, r2


data = load_data()
random.Random(RANDOM_SEED).shuffle(data)

n = len(data)
train_end = int(n * 0.70)
validation_end = int(n * 0.85)

train = data[:train_end]
validation = data[train_end:validation_end]
test = data[validation_end:]

if not train or not validation or not test:
    raise ValueError("Not enough valid records for all three splits.")

slope, intercept = fit_linear_regression(train)

print("TOTAL VALID RECORDS:", n)
print("TRAINING RECORDS:", len(train))
print("VALIDATION RECORDS:", len(validation))
print("TESTING RECORDS:", len(test))
print()
print("MODEL TRAINED ON TRAINING DATA ONLY")
print("Slope:", round(slope, 6))
print("Intercept:", round(intercept, 6))
print("Model: completion = slope * age + intercept")

for name, subset in [
    ("VALIDATION", validation),
    ("TEST", test)
]:
    mae, rmse, r2 = evaluate(subset, slope, intercept)
    print()
    print(name, "RESULTS")
    print("MAE:", round(mae, 4))
    print("RMSE:", round(rmse, 4))
    print("R2:", round(r2, 4))

print()
print("NOTE: This is a local evaluation script, not a Hadoop MapReduce job.")