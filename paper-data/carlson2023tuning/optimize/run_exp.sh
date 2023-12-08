#!/bin/bash

# get input arguments
NRUN=$1
RUNID=$2
NUMWORKERS=$3

# check input arguments (NRUN should look like integer, RUNID can just be any arbitrary string, SAMPLERUNDIR needs to exist)
case $NRUN in
  ''|*[!0-9]*) echo "NRUN is invalid, exiting"; exit 1 ;;
esac
case $NUMWORKERS in
  ''|*[!0-9]*) echo "NUMWORKERS is invalid, exiting"; exit 1 ;;
esac

RUNDIR=$(echo "nrun${NRUN}_${RUNID}")
SAMPLEDIR=/global/homes/m/mcarlson/LandIce/ALITune/optimize/sampling/$RUNDIR
MODELDIR=/global/homes/m/mcarlson/LandIce/ALITune/optimize/modeling/$RUNDIR

source prepare_env.sh

cd sampling
source setup_sampling_phase.sh $NRUN $RUNID
python sampling_driver.py -nrun $NRUN -rundir $SAMPLEDIR -numworkers $NUMWORKERS
cd ../../modeling
source setup_modeling_phase.sh $NRUN $RUNID ../sampling/$RUNDIR
python modeling_driver.py -nrun $NRUN -rundir $MODELDIR
