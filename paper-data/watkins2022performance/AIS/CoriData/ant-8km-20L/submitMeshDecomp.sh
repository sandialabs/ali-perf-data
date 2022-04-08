#!/bin/bash -login

#SBATCH -A m1041
#SBATCH --job-name=MeshDecomp
#SBATCH --output=MeshDecomp.%j.out
#SBATCH --error=MeshDecomp.%j.err
#SBATCH --qos=regular
#SBATCH --constraint=haswell
#SBATCH --nodes=1
#SBATCH --time=00:05:00 

# Load modules
source ${HOME}/bin/cori_intel_hsw_modules.sh

# Trilinos bin path
TRILINOS_BIN_PATH=${SCRATCH}/LandIce/TrilinosBuilds/build-intel-hsw-serial/install/bin

# Root path
ROOT_PATH=${SCRATCH}/LandIce/AIS/WeakScaling/Scale2D/ant-8km-20L

# Run decomp
#srun -n1 ${TRILINOS_BIN_PATH}/decomp --processors 128 --root ${ROOT_PATH}/ --subdir mesh-decomp mesh/antarctica_2d.exo
srun -n1 ${TRILINOS_BIN_PATH}/decomp --processors 256 --root ${ROOT_PATH}/ --subdir mesh-decomp mesh/antarctica_2d.exo

