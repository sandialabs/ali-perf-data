#!/bin/bash
cd blake_nightly_data 
now=$(date +"%Y%m%d")
FILE=ctest-$now.json
echo $FILE
if test -f "$FILE"; then
  echo "$FILE file exists"
  rm index11 
  cat index1 blake_nightly_data/html_entry >& index11
  mv index11 index1
  cat index1 index2 >& index.html
  git add index.html index1 
  git commit -m "Adding html entry from nightly tests."
  git push
else 
  echo "$FILE does not exist! Not updating index.html."
fi
