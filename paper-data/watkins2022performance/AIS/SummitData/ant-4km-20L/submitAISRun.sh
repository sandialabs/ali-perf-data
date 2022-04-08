#!/bin/bash

#BSUB -P CLI115
#BSUB -J AISRun
#BSUB -o AISRun.%J.out
#BSUB -e AISRun.%J.err
#BSUB -q batch
#BSUB -nnodes 16
#BSUB -W 30

# Load modules
source ${HOME}/bin/summit_gcc_modules.sh

# Case settings
NUMSAMPLES=10

# GPU Env variables
APPDIR=/gpfs/alpine/scratch/jwatkins/cli115/LandIce/AlbanyBuilds/build-summit-cuda-gcc-sfad16/src
JSRUNCONF="-n96 -a1 -c1 -g1 -M \"-gpu\""
export CUDA_LAUNCH_BLOCKING=1
#unset CUDA_LAUNCH_BLOCKING
export TPETRA_ASSUME_CUDA_AWARE_MPI=0

# Warmup
jsrun ${JSRUNCONF} ${APPDIR}/Albany input_albany_MueLuKokkos.yaml |& tee out-ant4k20L.v100.warmup.txt
mv out-ant4k20L.v100.warmup.txt timer_data/out-ant4k20L.v100.warmup.txt

# Run cases
for (( sid=0; sid<${NUMSAMPLES}; sid++ ))
do
  jsrun ${JSRUNCONF} ${APPDIR}/Albany input_albany_MueLuKokkos.yaml |& tee out-ant4k20L.v100.${sid}.txt
  mv out-ant4k20L.v100.${sid}.txt timer_data/out-ant4k20L.v100.${sid}.txt
done

# CPU Env variables
APPDIR=/gpfs/alpine/scratch/jwatkins/cli115/LandIce/AlbanyBuilds/build-summit-serial-gcc-sfad16/src
JSRUNCONF='-n672 -a1 -c1'

# Warmup
jsrun ${JSRUNCONF} ${APPDIR}/Albany input_albany_MueLu.yaml |& tee out-ant4k20L.pwr9.warmup.txt
mv out-ant4k20L.pwr9.warmup.txt timer_data/out-ant4k20L.pwr9.warmup.txt

# Run cases
for (( sid=0; sid<${NUMSAMPLES}; sid++ ))
do
  jsrun ${JSRUNCONF} ${APPDIR}/Albany input_albany_MueLu.yaml |& tee out-ant4k20L.pwr9.${sid}.txt
  mv out-ant4k20L.pwr9.${sid}.txt timer_data/out-ant4k20L.pwr9.${sid}.txt
done

