#!/bin/bash

machineName=$1 
PWD=`pwd`
dataDir="$PWD/$1_nightly_data" 
echo $dataDir 
cd $dataDir 
git reset --hard origin/master
git pull 
if [ "$machineName" == "waterman" ]; then 
  FILE=Ali_PerfTestsWaterman.ipynb
fi 
if [ "$machineName" == "blake" ]; then 
  FILE=Ali_PerfTestsBlake.ipynb
fi 
jupyter nbconvert --execute $FILE 
bash append_date.sh >& append_date.out
cd ../ 
