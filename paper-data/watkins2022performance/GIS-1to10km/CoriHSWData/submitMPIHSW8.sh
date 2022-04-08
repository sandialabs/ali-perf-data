#!/bin/bash

#SBATCH -A m1041
#SBATCH --job-name=MALIHSW
#SBATCH --output=MALIHSW.%j.out
#SBATCH --error=MALIHSW.%j.err
#SBATCH --constraint=haswell
#SBATCH --nodes=8
#SBATCH --switches=1
#SBATCH --qos=regular
#SBATCH --time=03:00:00 
#SBATCH --mail-user=jwatkin@sandia.gov
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL

# Load modules
source ${HOME}/bin/cori_intel_hsw_modules.sh

# Env variables
APPDIR=${SCRATCH}/LandIce/MALIBuilds/build-intel-hsw-serial-sfad12
SRUNCONF='--ntasks=256 --ntasks-per-node=32 --cpu-bind=cores --hint=nomultithread'

# Case settings
NUMSAMPLES=10
CASES=("1ws" "mem")

# Warmup
cp input_albany_mem.yaml albany_input.yaml
srun ${SRUNCONF} ${APPDIR}/landice_model
cp log.albany.timers.out timer_data/log.albany.timers.warmup.out
cp log.landice.0000.out timer_data/log.landice.timers.warmup.out
rm log.*

# Run cases
for (( sid=0; sid<${NUMSAMPLES}; sid++ ))
do
  for (( cid=0; cid<${#CASES[@]}; cid++ ))
  do
    case="${CASES[cid]}"
    cp input_albany_${case}.yaml albany_input.yaml
    srun ${SRUNCONF} ${APPDIR}/landice_model
    cp log.albany.timers.out timer_data/log.albany.timers.${case}.${sid}.out
    cp log.landice.0000.out timer_data/log.landice.timers.${case}.${sid}.out
    rm log.*
  done
done

