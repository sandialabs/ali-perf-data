#!/bin/bash

# get input arguments
NRUN=$1
RUNID=$2
SAMPLERUNDIR=$3

# check input arguments (NRUN should look like integer, RUNID can just be any arbitrary string, SAMPLERUNDIR needs to exist)
case $NRUN in
    ''|*[!0-9]*) echo "NRUN is invalid, exiting"; exit 1 ;;
esac
if [ ! -d $SAMPLERUNDIR ]  || [ -z $SAMPLERUNDIR ]; then
    echo "SAMPLERUNDIR does not exist or was not supplied, exiting"
    exit 1
fi

RUNDIR=$(echo "nrun${NRUN}_${RUNID}")

cd ..
source prepare_env.sh
cd modeling

if [ ! -d $RUNDIR ]; then
    mkdir $RUNDIR
    cp ../drivers/modeling_driver.py $RUNDIR/modeling_driver.py
    cp ../drivers/albany_driver.py $RUNDIR/albany_driver.py
    cp ../drivers/albany_tune_RCI.py $RUNDIR/albany_tune_RCI.py
    cp ../drivers/timeout.py $RUNDIR/timeout.py
    cp -r $SAMPLERUNDIR/gptune.db $RUNDIR/
    cp -r $SAMPLERUNDIR/.gptune $RUNDIR/
    cd $RUNDIR
    mkdir data
else
    cd $RUNDIR
fi

#python modeling_driver.py $NRUN $RUNDIR
