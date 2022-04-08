#!/bin/bash

#BSUB -P CLI115
#BSUB -J PopMesh
#BSUB -o PopMesh.%J.out
#BSUB -e PopMesh.%J.err
#BSUB -q batch
#BSUB -nnodes 16
#BSUB -W 5

# Load modules
source ${HOME}/bin/summit_gcc_modules.sh

# Location of executable, inputfile and profiling tool
APPDIR=/gpfs/alpine/scratch/jwatkins/cli115/LandIce/AlbanyBuilds/build-summit-serial-gcc-sfad16/src

# Env vars
export CUDA_LAUNCH_BLOCKING=1
#unset CUDA_LAUNCH_BLOCKING
export TPETRA_ASSUME_CUDA_AWARE_MPI=0

# Run
jsrun -n672 -a1 -c1 ${APPDIR}/Albany input_albany_PopulateMesh.yaml

