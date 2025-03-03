#!/bin/bash

#BSUB -P CLI115
#BSUB -J PopMesh
#BSUB -o PopMesh.%J.out
#BSUB -e PopMesh.%J.err
#BSUB -q batch
#BSUB -nnodes 256
#BSUB -W 10

# Load modules
source ${HOME}/bin/summit_gcc_modules.sh

# Location of executable, inputfile and profiling tool
APPDIR=/gpfs/alpine/scratch/jwatkins/cli115/LandIce/AlbanyBuilds/build-summit-cuda-gcc-sfad16/src

# Env vars
export CUDA_LAUNCH_BLOCKING=1
#unset CUDA_LAUNCH_BLOCKING
export TPETRA_ASSUME_CUDA_AWARE_MPI=0

# Run
jsrun -n1536 -a1 -c1 -g1 ${APPDIR}/Albany input_albany_PopulateMesh.yaml

