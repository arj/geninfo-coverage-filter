#!/bin/bash

TEST_FILE=test_files/main_coverage.info
EXPECTED_FILE=test_files/hidden_branch_filtered_coverage.info

../filter_coverage.py --filter_non_visible_branches $TEST_FILE > test_filtered.info.out

diff $EXPECTED_FILE test_filtered.info.out
RES=$?
rm test_filtered.info.out

if [ $RES -eq 0 ]; then
    echo "OK"
else
    echo "Test failed"
fi
