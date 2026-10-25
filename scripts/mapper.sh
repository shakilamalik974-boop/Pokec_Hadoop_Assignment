#!/bin/bash
awk -F '\t' 'NF == 60 && $3 ~ /^[0-9]+([.][0-9]+)?$/ { print "completion\t" $3 }'