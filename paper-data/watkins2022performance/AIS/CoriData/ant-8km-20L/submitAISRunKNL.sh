#!/bin/bash -login

## SBATCH -A m1041
#SBATCH -A m1795
#SBATCH --job-name=AISRun
#SBATCH --output=AISRun.%j.out
#SBATCH --error=AISRun.%j.err
#SBATCH --constraint=knl,quad,cache
#SBATCH --nodes=4
#SBATCH --switches=1
#SBATCH --qos=regular
#SBATCH --time=00:40:00
#SBATCH --mail-user=jwatkin@sandia.gov
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL

# Load modules
source ${HOME}/bin/cori_intel_knl_modules.sh

# Env variables
APPDIR=${SCRATCH}/LandIce/AlbanyBuilds/build-intel-knl-serial-sfad16/src
SRUNCONF='--ntasks=256 --ntasks-per-node=64 --cpu-bind=cores --hint=nomultithread'

# Case settings
NUMSAMPLES=10

# Warmup
srun ${SRUNCONF} ${APPDIR}/Albany input_albany_MueLu.yaml >& out-ant8k20L.knl.warmup.txt
mv out-ant8k20L.knl.warmup.txt knl_timer_data/out-ant8k20L.knl.warmup.txt

# Run cases
for (( sid=0; sid<${NUMSAMPLES}; sid++ ))
do
  srun ${SRUNCONF} ${APPDIR}/Albany input_albany_MueLu.yaml >& out-ant8k20L.knl.${sid}.txt
  mv out-ant8k20L.knl.${sid}.txt knl_timer_data/out-ant8k20L.knl.${sid}.txt
done

