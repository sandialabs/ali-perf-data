#!/bin/bash -login

#SBATCH -A m1041
#SBATCH --job-name=PopMesh
#SBATCH --output=PopMesh.%j.out
#SBATCH --error=PopMesh.%j.err
#SBATCH --constraint=haswell
#SBATCH --nodes=4
#SBATCH --qos=regular
#SBATCH --time=00:05:00 

# Load modules
source ${HOME}/bin/cori_intel_hsw_modules.sh

# Env variables
APPDIR=${SCRATCH}/LandIce/AlbanyBuilds/build-intel-hsw-serial-sfad16/src
SRUNCONF='--ntasks=128 --ntasks-per-node=32 --ntasks-per-socket=16 --cpu-bind=cores --hint=nomultithread'

# Run Case
srun ${SRUNCONF} ${APPDIR}/Albany input_albany_PopulateMesh.yaml

