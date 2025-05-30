#!/bin/bash

echo "==== Log Summary (Processed + Exact Matches) ===="

for file in *.txt; do
    echo "==> $file <=="
    grep -E "Processed [0-9]+ valid rows|Exact matches:" "$file"
    echo
done

