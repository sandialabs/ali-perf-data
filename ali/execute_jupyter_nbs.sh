#!/bin/bash

machineName=$1
if [ "$machineName" == "waterman" ]; then 
  FILE=Ali_PerfTestsWaterman.ipynb
  FILE2=Comparison_Interactive.ipynb
fi 
if [ "$machineName" == "blake" ]; then 
  FILE=Ali_PerfTestsBlake.ipynb
  FILE2=Comparison_Interactive.ipynb
fi 
if [ "$machineName" == "weaver" ]; then 
  FILE=Ali_PerfTestsWeaver.ipynb
  FILE2=Comparison_Interactive.ipynb
fi 

echo "Executing ${FILE} and converting to html..."
PWD=`pwd`
dataDir="$PWD/${machineName}_nightly_data"
cd $dataDir
jupyter nbconvert --ExecutePreprocessor.timeout=300 --execute $FILE

echo "Executing ${FILE2} and converting to html..."
jupyter nbconvert --ExecutePreprocessor.timeout=300 --execute $FILE2

echo "####### Running append_date.sh for ${machineName} #######"
source append_date.sh
cd ../ 

