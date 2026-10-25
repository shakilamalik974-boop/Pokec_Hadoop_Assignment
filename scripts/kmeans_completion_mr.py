import sys
import math


def mapper():
    if len(sys.argv) != 3:
     sys.exit("Usage: kmeans_completion_mr.py mapper centroids.txt")

    centroids = []
    with open(sys.argv[2], "r") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= 2:
                centroids.append((int(parts[0]), float(parts[1])))

    for line in sys.stdin:
        cols = line.rstrip("\n").split("\t")
        if len(cols) < 8:
            continue

        try:
            completion = float(cols[2])
            age = float(cols[7])

            if (math.isnan(age) or math.isinf(age) or
                    not 1 <= age <= 100):
                continue

            if (math.isnan(completion) or math.isinf(completion) or
                    not 0 <= completion <= 100):
                continue

            cluster = min(
                centroids,
                key=lambda item: abs(age - item[1])
            )[0]

            print("%d\t%.6f" % (cluster, completion))

        except (ValueError, IndexError):
            continue


def reducer():
    totals = {}

    for line in sys.stdin:
        parts = line.strip().split("\t")
        if len(parts) != 2:
            continue

        try:
            cluster = int(parts[0])
            completion = float(parts[1])
        except ValueError:
            continue

        if cluster not in totals:
            totals[cluster] = [0, 0.0]

        totals[cluster][0] += 1
        totals[cluster][1] += completion

    for cluster in sorted(totals):
        count, total_completion = totals[cluster]
        average = total_completion / count
        print("Cluster %d: users=%d, average_completion=%.2f%%" %
              (cluster, count, average))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: kmeans_completion_mr.py mapper|reducer ...")

    if sys.argv[1] == "mapper":
        mapper()
    elif sys.argv[1] == "reducer":
        reducer()
    else:
        sys.exit("Argument must be mapper or reducer")