import csv
import os
from collections import defaultdict

INPUT_FILE = "data/pokec_100.txt"
OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(
    OUTPUT_DIR, "completion_relationships.csv"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

age_groups = defaultdict(list)
gender_groups = defaultdict(list)
valid_rows = 0
invalid_rows = 0

with open(INPUT_FILE, "r", encoding="utf-8", newline="") as file:
    reader = csv.reader(file, delimiter="\t")

    for row in reader:
        if len(row) != 60:
            invalid_rows += 1
            continue

        try:
            completion = float(row[2].strip())
            age = float(row[7].strip())
        except (ValueError, IndexError):
            invalid_rows += 1
            continue

        if not (0 <= completion <= 100 and 0 < age <= 120):
            invalid_rows += 1
            continue

        gender = row[3].strip() or "Missing"

        age_group = (
            "Under 20" if age < 20
            else "20-24" if age < 25
            else "25-29" if age < 30
            else "30 and above"
        )

        age_groups[age_group].append(completion)
        gender_groups[gender].append(completion)
        valid_rows += 1

with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Feature", "Category", "Users", "Average Completion"])

    for group, values in age_groups.items():
        writer.writerow([
            "Age group", group, len(values),
            round(sum(values) / len(values), 2)
        ])

    for group, values in gender_groups.items():
        writer.writerow([
            "Gender", group, len(values),
            round(sum(values) / len(values), 2)
        ])

print("=== Completion Relationship Analysis ===")
print("Valid records analyzed:", valid_rows)
print("Skipped records:", invalid_rows)

print("\nAverage completion by age group:")
for group, values in age_groups.items():
    print(f"{group}: {sum(values) / len(values):.2f}% ({len(values)} users)")

print("\nAverage completion by gender code:")
for group, values in gender_groups.items():
    print(f"{group}: {sum(values) / len(values):.2f}% ({len(values)} users)")

print("\nCSV saved to:", OUTPUT_FILE)