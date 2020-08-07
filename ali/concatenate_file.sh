#!/bin/bash

machineName=$1 
now=$(date +"%m_%d_%Y")
if [ "$machineName" == "waterman" ]; then 
  FILE=Ali_PerfTestsWaterman_$now.html
fi 
if [ "$machineName" == "blake" ]; then 
  FILE=Ali_PerfTestsBlake_$now.html
fi 
if [ "$machineName" == "weaver" ]; then 
  FILE=Ali_PerfTestsWeaver_$now.html
fi 

PWD=`pwd`
dataDir="$PWD/${machineName}_nightly_data"
if test -f "${dataDir}/${FILE}"; then
  echo "$FILE file exists"
  i1=index1_$machineName
  ee=""$machineName"_nightly_data/html_entry"
  cat $i1 $ee >& index11
  mv index11 $i1
  html="index_$machineName.html"
  cat $i1 index2 >& $html

  echo "Checking in ${html} and ${i1}..."
  git add $html $i1
  if [ "$machineName" == "waterman" ]; then 
    git commit -m "Adding html entry from Ali waterman nightly tests."
  fi 
  if [ "$machineName" == "blake" ]; then 
    git commit -m "Adding html entry from Ali blake nightly tests."
  fi 
  if [ "$machineName" == "weaver" ]; then 
    git commit -m "Adding html entry from Ali weaver nightly tests."
  fi 
  git push
else 
  echo "$FILE does not exist! Not updating index.html."
fi

