#!/bin/bash -login

## SBATCH -A m1041
#SBATCH -A m1795
#SBATCH --job-name=PopMesh
#SBATCH --output=PopMesh.%j.out
#SBATCH --error=PopMesh.%j.err
#SBATCH --constraint=knl,quad,cache
#SBATCH --nodes=256
#SBATCH --qos=regular
#SBATCH --time=00:30:00
#SBATCH --mail-user=jwatkin@sandia.gov
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL

# Load modules
source ${HOME}/bin/cori_intel_knl_modules.sh

# Env variables
APPDIR=${SCRATCH}/LandIce/AlbanyBuilds/build-intel-knl-serial-sfad16/src
SRUNCONF='--ntasks=16384 --ntasks-per-node=64 --cpu-bind=cores --hint=nomultithread'

# Run Case
srun ${SRUNCONF} ${APPDIR}/Albany input_albany_PopulateMesh.yaml

