#!/bin/bash

machineName=$1
if [ "$machineName" == "weaver" ]; then 
  FILE=Ali_PerfTestsWeaver.ipynb
  FILE2=Ali_PerfTestsWeaver.html
fi 
if [ "$machineName" == "blake" ]; then 
  FILE=Ali_PerfTestsBlake.ipynb
  FILE2=Ali_PerfTestsBlake.html
fi 

echo "Executing ${FILE} and converting to html..."
PWD=`pwd`
dataDir="$PWD/${machineName}_nightly_data"
cd $dataDir
jupyter nbconvert --to html --TemplateExporter.exclude_input=True --ExecutePreprocessor.timeout=600 --execute $FILE

echo "####### Running append_date.sh for ${machineName} #######"
if test -f "${FILE2}"; then
  source append_date.sh
else 
  echo "${FILE2} does not exist! Not running append_date.sh"
fi
cd ../ 

