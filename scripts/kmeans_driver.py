import os
import subprocess

PROJECT_DIR = r"E:\Pokec_Hadoop_Assignment"
SCRIPTS_DIR = os.path.join(PROJECT_DIR, "scripts")
LOCAL_CENTROIDS = os.path.join(SCRIPTS_DIR, "centroids.txt")
MAPPER_SCRIPT = os.path.join(SCRIPTS_DIR, "mapreduce_clustering.py")
ITERATION_OUTPUT = os.path.join(SCRIPTS_DIR, "kmeans_iteration_output.txt")

CONTAINER = "pokec-namenode"
HDFS_INPUT = "/pokec/input/pokec_100.txt"
HDFS_WORK = "/pokec/kmeans_work"
HDFS_OUTPUT_BASE = "/pokec/kmeans_iterations"

MAX_ITERATIONS = 20
TOLERANCE = 0.001
STREAMING_JAR = "/opt/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.6.jar"


def run_command(command):
    print("\nRunning:", " ".join(command))
    subprocess.run(command, check=True)


def read_centroids(path):
    centroids = {}
    with open(path, "r") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= 2:
                centroids[int(parts[0])] = float(parts[1])
    if not centroids:
        raise RuntimeError("Centroids file is empty or invalid.")
    return centroids


def write_centroids(path, centroids):
    with open(path, "w") as f:
        for cluster in sorted(centroids):
            f.write("%d\t%.6f\n" % (cluster, centroids[cluster]))


def main():
    centroids = read_centroids(LOCAL_CENTROIDS)

    run_command([
        "docker", "cp", MAPPER_SCRIPT,
        CONTAINER + ":/tmp/mapreduce_clustering.py"
    ])

    for iteration in range(1, MAX_ITERATIONS + 1):
        print("\n=== K-Means iteration %d ===" % iteration)

        hdfs_output = "%s/iter_%02d" % (HDFS_OUTPUT_BASE, iteration)

        run_command([
            "docker", "cp", LOCAL_CENTROIDS,
            CONTAINER + ":/tmp/centroids.txt"
        ])

        subprocess.run([
            "docker", "exec", CONTAINER, "hdfs", "dfs", "-mkdir", "-p",
            HDFS_WORK
        ], check=True)

        subprocess.run([
            "docker", "exec", CONTAINER, "hdfs", "dfs", "-rm", "-f",
            HDFS_WORK + "/centroids.txt"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        run_command([
            "docker", "exec", CONTAINER, "hdfs", "dfs", "-put",
            "/tmp/centroids.txt", HDFS_WORK + "/centroids.txt"
        ])

        subprocess.run([
            "docker", "exec", CONTAINER, "hdfs", "dfs", "-rm", "-r", "-f",
            hdfs_output
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        streaming_command = (
            "hadoop jar " + STREAMING_JAR +
            " -D mapreduce.framework.name=local" +
            " -files /tmp/mapreduce_clustering.py,/tmp/centroids.txt" +
            " -input " + HDFS_INPUT +
            " -output " + hdfs_output +
            " -mapper 'python mapreduce_clustering.py mapper centroids.txt'" +
            " -reducer 'python mapreduce_clustering.py reducer'"
        )

        run_command([
            "docker", "exec", CONTAINER, "bash", "-lc",
            streaming_command
        ])

        run_command([
            "docker", "exec", CONTAINER, "hdfs", "dfs", "-get", "-f",
            hdfs_output + "/part-00000", "/tmp/kmeans_centroids.txt"
        ])

        run_command([
            "docker", "cp",
            CONTAINER + ":/tmp/kmeans_centroids.txt", ITERATION_OUTPUT
        ])

        new_centroids = {}
        with open(ITERATION_OUTPUT, "r") as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) >= 2:
                    new_centroids[int(parts[0])] = float(parts[1])

        if not new_centroids:
            raise RuntimeError("No centroids returned by MapReduce.")

        for cluster in centroids:
            if cluster not in new_centroids:
                new_centroids[cluster] = centroids[cluster]

        shifts = [
            abs(new_centroids[c] - centroids[c])
            for c in centroids
        ]
        max_shift = max(shifts) if shifts else 0.0

        centroids = new_centroids
        write_centroids(LOCAL_CENTROIDS, centroids)

        print("Updated centroids:", centroids)
        print("Maximum centroid shift:", max_shift)

        if max_shift < TOLERANCE:
            print("Converged after %d iterations." % iteration)
            break

    print("\nFinal centroids saved to:", LOCAL_CENTROIDS)


if __name__ == "__main__":
    main()