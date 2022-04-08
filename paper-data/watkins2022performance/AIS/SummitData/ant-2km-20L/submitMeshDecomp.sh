#!/bin/bash

#BSUB -P CLI115
#BSUB -J MeshDecomp
#BSUB -o MeshDecomp.%J.out
#BSUB -e MeshDecomp.%J.err
#BSUB -q batch
#BSUB -nnodes 1
#BSUB -W 5

# Load modules
source ${HOME}/bin/summit_gcc_modules.sh

# Trilinos bin path
TRILINOS_BIN_PATH=/gpfs/alpine/scratch/jwatkins/cli115/LandIce/TrilinosBuilds/build-summit-serial-gcc/install/bin

# Root path
ROOT_PATH=/gpfs/alpine/scratch/jwatkins/cli115/LandIce/AIS/WeakScaling/Scale2D/ant-2km-20L

# Run decomp
#jsrun -n1 -a1 -c1 -g1 ${TRILINOS_BIN_PATH}/decomp --processors 384 --root ${ROOT_PATH}/ --subdir mesh-decomp mesh/antarctica_2d.exo
jsrun -n1 -a1 -c1 -g1 ${TRILINOS_BIN_PATH}/decomp --processors 2688 --root ${ROOT_PATH}/ --subdir mesh-decomp mesh/antarctica_2d.exo

