#!/bin/bash

machineName=$1
alias jupyter=/usr/local/bin/jupyter 
PWD=`pwd`
dataDir="$PWD/$1_nightly_data" 
echo $dataDir 
cd $dataDir 
git reset --hard origin/master
git pull
cd ../../ext/kcshan-perf-analysis 
git reset --hard origin/master
git pull 
cd ../../ali/$1_nightly_data
if [ "$machineName" == "waterman" ]; then 
  FILE=Ali_PerfTestsWaterman.ipynb
  FILE2=Comparison_Interactive.ipynb
fi 
if [ "$machineName" == "blake" ]; then 
  FILE=Ali_PerfTestsBlake.ipynb
  FILE2=Comparison_Interactive.ipynb
fi 
jupyter nbconvert --execute $FILE 
jupyter nbconvert --execute $FILE2 
bash append_date.sh >& append_date.out
cd ../ 
