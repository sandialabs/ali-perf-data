#!/bin/bash

now=$(date +"%Y%m%d")
FILE=ctest-$now.json
if test -f "$FILE"; then
  echo "$FILE file exists"
  now=$(date +"%m_%d_%Y")
  mv Ali_PerfTestsBlake.html Ali_PerfTestsBlake_$now.html
  mv Comparison_Interactive.html Comparison_Interactive_$now.html

  echo "Checking in Ali_PerfTestsBlake_${now}.html and Comparison_Interactive_${now}.html..."
  git add Ali_PerfTestsBlake_$now.html
  git add Comparison_Interactive_$now.html 
  git commit -m "Checking in Blake Jupyter notebooks from $now ." 
  git push
  rm html_entry 
  echo "<li><p><strong><a href="blake_nightly_data/Ali_PerfTestsBlake_$now.html">$now</a></strong>.</p>" >& html_entry
else  
  echo "$FILE does not exist! Jupyter notebook htmls will not be pushed."
fi
