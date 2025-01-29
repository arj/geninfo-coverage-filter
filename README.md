# C/C++ branch coverage filtering

The typical workflow is
```
$ g++ --coverage -g -O0 main.cpp
$ lcov -z --directory .
$ lcov --rc lcov_branch_coverage=1 --capture --directory . --output-file main_coverage.info
$ genhtml --branch-coverage main_coverage.info --output-directory out
```
However, the result contains lines which do not have any visible branches (e.g. a return statement).
These branches are created internally e.g. for exception handling.

This small python script parses the coverage info file generated by lcov and filters
(by checking if at the corresponding line there is an if, while, etc.) those branch coverage measurements
which do NOT have a corresponding line.

# Example for use

```
$ ./filter_coverage.py --filter_non_visible_branches main_coverage.info > filtered_main_coverage.info
$ # Now we can call genhtml as before
$ genhtml --branch-coverage main_coverage.info --output-directory out
```
