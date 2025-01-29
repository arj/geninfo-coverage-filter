#!/bin/bash

TEST_FILE=test_files/main_coverage.info

../filter_coverage.py $TEST_FILE > test_filtered.info

diff $TEST_FILE test_filtered.info
RES=$?
rm test_filtered.info

if [ $RES -eq 0 ]; then
    echo "OK"
else
    echo "Test failed"
fi
