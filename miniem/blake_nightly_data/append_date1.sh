#!/bin/bash

now=$(date +"%Y%m%d")
FILE=ctest-$now.json
echo $FILE
if test -f "$FILE"; then
    echo "$FILE exist"
fi
