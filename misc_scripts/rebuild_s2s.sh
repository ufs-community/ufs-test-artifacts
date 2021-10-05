#!/bin/bash -l

set -x
newtag=$1
$ufs_location=$2
$machine=$3
$module_location=$4
$test_name=$5
$ufs_artifacts_location=$6
cd $ufs_location
rm -rf ufs-weather-model
git clone --recurse-submodules git@github.com:ufs-community/ufs-weather-model
cd ufs-weather-model
sed -i 's/module load esmf/#module load esmf/g' modulefiles/ufs_common
cp ../config/fv3_slurm.IN_$machine tests/fv3_conf
cp ../rt.prof tests
#load the modules with new esmf tag
export ESMFMKFILE=`find $module_location -iname esmf.mk | /usr/bin/grep $newtag`
sed -i "s/esmftag/$newtag/g" tests/rt.prof
cd tests
./rt.sh -k -l rt.prof
runroot=`grep RUNDIR_ROOT log_$machine.intel/run_$test_name | grep export | awk -F "=" '{print $2}'`
jobid=`grep -Ri jobid log_$machine.intel/* | head -n 1 | awk -F " " '{print $11}'`
cd /work/noaa/stmp/mpotts/ufs-test-artifacts
python3 ./python_scripts/archive_results.py -y config/ufs-$machine -j $jobid -t $newtag -D $runroot/$test_name
rm -rf $runroot
