#!/bin/bash

cd waterman_nightly_data
git reset --hard origin/master
git pull 
jupyter nbconvert --execute Ali_PerfTestsWaterman.ipynb
bash append_date.sh >& append_date.out 
