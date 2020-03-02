#!/bin/bash

machineName=$1 
PWD=`pwd`
dataDir="$PWD/$1_nightly_data" 
cd $dataDir 
now=$(date +"%m_%d_%Y")
echo $now 
if [ "$machineName" == "waterman" ]; then 
  FILE=Ali_PerfTestsWaterman_$now.html
fi 
if [ "$machineName" == "blake" ]; then 
  FILE=Ali_PerfTestsBlake_$now.html
fi 
echo $FILE 
if test -f "$FILE"; then
  echo "$FILE file exists"
  i1=index1_$machineName
  ee=""$machineName"_nightly_data/html_entry"
  cat $i1 $ee >& index11
  mv index11 $i1
  html="index_$machineName.html"
  cat $i1 index2 >& $html
  git add $html $i1
  if [ "$machineName" == "waterman" ]; then 
    git commit -m "Adding html entry from Ali waterman nightly tests."
  fi 
  if [ "$machineName" == "blake" ]; then 
    git commit -m "Adding html entry from Ali blake nightly tests."
  fi 
  git push
else 
  echo "$FILE does not exist! Not updating index.html."
fi
