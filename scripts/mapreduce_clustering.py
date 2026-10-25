import sys
import math


def mapper():
    """Assign each valid age to its nearest centroid."""
    if len(sys.argv) != 3:
        sys.exit("Usage: mapreduce_clustering.py mapper centroids_file")

    centroids_file = sys.argv[2]

    centroids = []
    with open(centroids_file, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                cluster, centroid = line.split("\t")
                centroids.append((int(cluster), float(centroid)))

    if not centroids:
        sys.exit("No centroids found")

    for line in sys.stdin:
        cols = line.rstrip("\n").split("\t")
        if len(cols) < 8:
            continue

        try:
            user_id = cols[0]
            age = float(cols[7])

            if math.isnan(age) or math.isinf(age) or not 1 <= age <= 100:
                continue

            cluster = min(
                centroids,
                key=lambda item: abs(age - item[1])
            )[0]

            print("%d\t%.6f\t%s" % (cluster, age, user_id))

        except (ValueError, IndexError):
            continue


def reducer():
    """Calculate a new mean age for every cluster."""
    totals = {}

    for line in sys.stdin:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 3:
            continue

        try:
            cluster = int(parts[0])
            age = float(parts[1])
        except ValueError:
            continue

        if cluster not in totals:
            totals[cluster] = [0, 0.0]

        totals[cluster][0] += 1
        totals[cluster][1] += age

    for cluster in sorted(totals):
        count, age_sum = totals[cluster]
        new_centroid = age_sum / count
        print("%d\t%.6f\t%d" % (cluster, new_centroid, count))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: mapreduce_clustering.py mapper|reducer ...")

    if sys.argv[1] == "mapper":
        mapper()
    elif sys.argv[1] == "reducer":
        reducer()
    else:
        sys.exit("Argument must be mapper or reducer")