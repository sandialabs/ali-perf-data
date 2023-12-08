export CONFIGDIR=/global/homes/m/mcarlson/LandIce/perlmutter-config
export GPTUNEROOT=/global/homes/m/mcarlson/LandIce/GPTune
export EXPDIR=/global/homes/m/mcarlson/LandIce/ALITune/optimize

cd $CONFIGDIR
source prlm_gcc_modules.sh
module load python
cd $GPTUNEROOT
source run_env.sh
cd $CONFIGDIR
source pytrilinos_setup_cuda_gcc.sh
cd $EXPDIR

