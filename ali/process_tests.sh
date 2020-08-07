#!/bin/bash

if [[ $# -eq 0 ]]; then 
  echo "No arguments provided to process_tests.sh!"
  exit 1 
fi 

machineName=$1 
if [ "$machineName" != "weaver" ]; then 
  if [ "$machineName" != "blake" ]; then 
    echo "Invalid machine name!  Valid names are 'blake' and 'weaver'.  You specified " $machineName 
    exit 1 
  fi 
fi 

echo "####### Running process_tests.sh ${machineName} #######"
echo "Pull the latest from ikalash.github.io..."
git reset --hard origin/master
git checkout master
git pull origin master

echo "Pull the latest from kcshan-perf-analysis..."
cd ../ext/kcshan-perf-analysis
git reset --hard origin/master
git checkout master
git pull origin master
git submodule init 
git submodule update 

echo "####### Running execute_jupyter_nbs.sh ${machineName} #######"
cd ../../ali 
source execute_jupyter_nbs.sh $machineName

echo "####### Running concatenate_file.sh ${machineName} #######"
source concatenate_file.sh $machineName

echo "####### Running email_report.py for ${machineName} #######"
PWD=`pwd`
dataDir=${PWD}/${machineName}_nightly_data
cd $dataDir
python email_report.py
cd ..

