#!/bin/bash

cd blake_nightly_ali_data
git pull 
jupyter nbconvert --execute Ali_PerfTestsBlake.ipynb
bash append_date.sh >& append_date.out 
