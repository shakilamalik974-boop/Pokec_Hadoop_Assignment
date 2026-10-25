#!/bin/bash
awk -F '\t' '
{
    v = $2 + 0
    if (NR == 1 || v < min) min = v
    if (NR == 1 || v > max) max = v
    sum += v
    count++
}
END {
    if (count > 0) {
        printf "Records analyzed: %d\n", count
        printf "Minimum completion: %.2f\n", min
        printf "Maximum completion: %.2f\n", max
        printf "Average completion: %.2f\n", sum/count
    }
}'