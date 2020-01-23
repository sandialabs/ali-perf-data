#!/bin/bash
cd waterman_nightly_data 
now=$(date +"%m_%d_%Y")
FILE=Ali_PerfTestsWaterman_$now.html
echo $FILE
if test -f "$FILE"; then
  echo "$FILE file exists"
  cd ../
  cat index1_waterman waterman_nightly_data/html_entry >& index1_waterman1
  mv index1_waterman1 index1_waterman
  cat index1_waterman index2 >& index_waterman.html
  git add index_waterman.html index1_waterman 
  git commit -m "Adding html entry from Ali nightly tests."
  git push
else 
  echo "$FILE does not exist! Not updating index_waterman.html."
fi
