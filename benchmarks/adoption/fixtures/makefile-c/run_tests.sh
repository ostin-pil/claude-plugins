#!/bin/sh
# Minimal smoke test: build output runs and prints the expected sum.
out=$(./thing)
if [ "$out" = "5" ]; then
    echo "ok"
    exit 0
fi
echo "FAIL: expected 5, got $out"
exit 1
