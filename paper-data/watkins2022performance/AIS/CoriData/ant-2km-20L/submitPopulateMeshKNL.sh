#!/bin/bash -login

#SBATCH -A m1041
#SBATCH --job-name=PopMesh
#SBATCH --output=PopMesh.%j.out
#SBATCH --error=PopMesh.%j.err
#SBATCH --constraint=knl,quad,cache
#SBATCH --nodes=64
#SBATCH --qos=regular
#SBATCH --time=00:10:00

# Load modules
source ${HOME}/bin/cori_intel_knl_modules.sh

# Env variables
APPDIR=${SCRATCH}/LandIce/AlbanyBuilds/build-intel-knl-serial-sfad16/src
SRUNCONF='--ntasks=4096 --ntasks-per-node=64 --cpu-bind=cores --hint=nomultithread'

# Run Case
srun ${SRUNCONF} ${APPDIR}/Albany input_albany_PopulateMesh.yaml

