#!/bin/bash

# get input arguments
NRUN=$1
RUNID=$2

# check input arguments (NRUN should look like integer, RUNID can just be any arbitrary string)
case $NRUN in
    ''|*[!0-9]*) echo "NRUN is invalid, exiting"; exit 1 ;;
esac

RUNDIR=$(echo "nrun${NRUN}_${RUNID}")

cd ..
source prepare_env.sh
cd sampling

if [ ! -d $RUNDIR ]; then
    mkdir $RUNDIR
    cp ../drivers/sampling_driver.py $RUNDIR/sampling_driver.py
    cp ../drivers/albany_driver.py $RUNDIR/albany_driver.py
    cp ../drivers/albany_tune_RCI.py $RUNDIR/albany_tune_RCI.py
    cp ../drivers/timeout.py $RUNDIR/timeout.py
    cd $RUNDIR
    mkdir data
    mkdir -p .gptune
    tp=Albany_LandIce_PRLM
    app_json=$(echo "{\"tuning_problem_name\":\"$tp\"")
    echo "$app_json$machine_json$software_json$loadable_machine_json$loadable_software_json}" | jq '.' > .gptune/meta.json
else
    cd $RUNDIR
fi

#python sampling_driver.py $NRUN $RUNDIR
