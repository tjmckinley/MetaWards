#!/bin/bash
#PBS -l walltime=01:00:00
#PBS -l select=4:ncpus=64
# The above sets 4 nodes with 64 cores each

# source the skeleton bashrc to make sure we have all variables that we need
source /home/metawards/OFFICIAL_SENSITIVE/bash_template

# source the version of metawards we want to use
source $METADIR/envs/metawards-devel/bin/activate

# change into the directory from which this job was submitted
cd $PBS_O_WORKDIR

# if you need to change the path to the MetaWardsData repository,
# then update the below line and uncomment
#export METAWARDSDATA="$METADIR/GitHub/MetaWardsData"

metawards --seed 15324 --additional ExtraSeedsBrighton.dat \
          --input ncovparams.csv --repeats 8 --nthreads 16
