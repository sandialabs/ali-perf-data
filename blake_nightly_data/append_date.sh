#!/bin/bash

now=$(date +"%m_%d_%Y")
echo $now
mv Blob_PerfTestsBlake.html Blob_PerfTestsBlake_$now.html
git add Blob_PerfTestsBlake_$now.html
git commit -m "Checking in jupyter notebook from $now" 
git push
rm html_entry 
echo "<li><p><strong><a href="blake_nightly_data/Blob_PerfTestsBlake_$now.html">$now</a></strong>.</p>" >& html_entry
