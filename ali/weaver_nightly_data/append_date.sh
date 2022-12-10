#!/bin/bash

now=$(date +"%Y%m%d")
FILE=ctest-${now}.json
if test -f "$FILE"; then
  echo "$FILE file exists"
  echo "Updating html..."
  old_date=`sed -e 's/.*Ali_PerfTestsWeaver_\(.*\).html.*/\1/' html_entry`
  mv Ali_PerfTestsWeaver_${old_date}.html ../../../archive-ali-perf-data/weaver_nightly_data/
  now=$(date +"%m_%d_%Y")
  mv Ali_PerfTestsWeaver.html Ali_PerfTestsWeaver_${now}.html
  mv html_entry html_entry_old
  echo "<li><p><strong><a href="weaver_nightly_data/Ali_PerfTestsWeaver_${now}.html">${now}</a></strong>.</p>" >& html_entry

  echo "Checking in Ali_PerfTestsWeaver_${now}.html..."
  git rm Ali_PerfTestsWeaver_${old_date}.html
  git add Ali_PerfTestsWeaver_${now}.html
  git add html_entry
  git commit -m "Checking in Weaver Jupyter notebooks from ${now} ." 
  git push
else  
  echo "$FILE does not exist! Jupyter notebook htmls will not be pushed."
  rm Ali_PerfTestsWeaver.html
fi
