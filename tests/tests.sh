#!/bin/bash

for f in test_*.sh; do
    echo -n "$f "
    ./$f
done
