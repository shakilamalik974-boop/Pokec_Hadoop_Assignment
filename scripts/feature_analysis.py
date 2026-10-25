import csv
from collections import Counter

FILE_PATH = "data/pokec_100.txt"

age_values = []
gender_counts = Counter()
region_counts = Counter()
valid_rows = 0
invalid_ages = 0

with open(FILE_PATH, "r", encoding="utf-8", newline="") as file:
    reader = csv.reader(file, delimiter="\t")

    for row in reader:
        if len(row) != 60:
            continue

        valid_rows += 1

        # Dataset field positions: AGE=column 8,
        # gender=column 4, region=column 5 (1-based)
        age = row[7].strip()
        gender = row[3].strip()
        region = row[4].strip()

        if age.isdigit() and 0 < int(age) <= 120:
            age_values.append(int(age))
        else:
            invalid_ages += 1

        gender_counts[gender or "Missing"] += 1
        region_counts[region or "Missing"] += 1

print("=== Pokec Feature Analysis ===")
print("Valid profile rows:", valid_rows)
print("Valid ages:", len(age_values))
print("Invalid/missing ages:", invalid_ages)

if age_values:
    print("Minimum age:", min(age_values))
    print("Maximum age:", max(age_values))
    print("Average age:", round(sum(age_values) / len(age_values), 2))

print("\nGender distribution:")
for category, count in gender_counts.most_common(10):
    print(repr(category), ":", count)

print("\nTop 10 regions:")
for category, count in region_counts.most_common(10):
    print(repr(category), ":", count)