#!/bin/bash -login

## SBATCH -A m1041
#SBATCH -A m1795
#SBATCH --job-name=AISRun
#SBATCH --output=AISRun.%j.out
#SBATCH --error=AISRun.%j.err
#SBATCH --constraint=haswell
#SBATCH --nodes=256
#SBATCH --switches=1
#SBATCH --qos=regular
#SBATCH --time=01:00:00 
#SBATCH --mail-user=jwatkin@sandia.gov
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL

# Load modules
source ${HOME}/bin/cori_intel_hsw_modules.sh

# Env variables
APPDIR=${SCRATCH}/LandIce/AlbanyBuilds/build-intel-hsw-serial-sfad16/src
SRUNCONF='--ntasks=8192 --ntasks-per-node=32 --ntasks-per-socket=16 --cpu-bind=cores --hint=nomultithread'

# Case settings
NUMSAMPLES=10

# Warmup
srun ${SRUNCONF} ${APPDIR}/Albany input_albany_MueLu.yaml >& out-ant1k20L.hsw.warmup.txt
mv out-ant1k20L.hsw.warmup.txt hsw_timer_data/out-ant1k20L.hsw.warmup.txt

# Run cases
for (( sid=0; sid<${NUMSAMPLES}; sid++ ))
do
  srun ${SRUNCONF} ${APPDIR}/Albany input_albany_MueLu.yaml >& out-ant1k20L.hsw.${sid}.txt
  mv out-ant1k20L.hsw.${sid}.txt hsw_timer_data/out-ant1k20L.hsw.${sid}.txt
done

