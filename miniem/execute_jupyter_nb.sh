#!/bin/bash

cd blake_nightly_data
git pull 
jupyter nbconvert --execute Blob_PerfTestsBlake.ipynb
bash append_date.sh >& append_date.out 
