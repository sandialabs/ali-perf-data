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

echo "Executing ${FILE} and converting to html..."
PWD=`pwd`
dataDir="$PWD/${machineName}_nightly_data"
cd $dataDir
jupyter nbconvert --execute $FILE

echo "Executing ${FILE2} and converting to html..."
jupyter nbconvert --execute $FILE2

echo "####### Running append_date.sh for ${machineName} #######"
source append_date.sh
cd ../ 

