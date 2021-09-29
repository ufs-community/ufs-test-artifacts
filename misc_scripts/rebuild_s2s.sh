#!/bin/bash -l

set -x
newtag=$1
cd  /work/noaa/da/mpotts/sandbox
rm -rf ufs-weather-model
git clone --recurse-submodules git@github.com:ufs-community/ufs-weather-model
cd ufs-weather-model
sed -i 's/module load esmf/#module load esmf/g' modulefiles/ufs_common
cp ~/fv3_slurm.IN_orion tests/fv3_conf
cp ~/rt.prof tests
#load the modules with new esmf tag
export ESMFMKFILE=`find /work/noaa/da/mpotts/sandbox/hpc-modules -iname esmf.mk | /usr/bin/grep $newtag`
sed -i "s/esmftag/$newtag/g" tests/rt.prof
cd tests
./rt.sh -k -l rt.prof
runroot=`grep RUNDIR_ROOT log_orion.intel/run_cpld_bmark_wave_v16.log | grep export | awk -F "=" '{print $2}'`
jobid=`grep -Ri jobid log_orion.intel/* | head -n 1 | awk -F " " '{print $11}'`
cd /work/noaa/stmp/mpotts/ufs-test-artifacts
python3 ./python_scripts/archive_results.py -y config/ufs-orion.yaml -j $jobid -t $newtag -D $runroot/cpld_bmark_wave_v16
rm -rf $runroot
