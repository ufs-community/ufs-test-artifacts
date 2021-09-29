#!/bin/bash -l

set -x
cd  /scratch1/NCEPDEV/da/Mark.Potts/sandbox/ufs-weather-model
#git remote update
#git pull origin develop
#git submodule init; git submodule sync; git submodule update; git submodule foreach git submodule init;git submodule foreach git submodule sync; git submodule foreach git submodule update
# remove old build directory and re-create
rm -rf build-new
mkdir build-new
#WW3 has build objects in source tree. remove and check back out from git
cd WW3
rm -rf *
git checkout -- *
cd ..
#load the modules with new esmf tag
module purge
module use $PWD/modulefiles
module load ufs_hera.intel
export tag=`grep esmf modulefiles/ufs_common | awk -F '/' '{print $2}'`
cd /scratch1/NCEPDEV/da/Mark.Potts/sandbox/ufs-weather-model/build-new
cmake -DMULTI_GASES=OFF -DMPI=ON -DCMAKE_BUILD_TYPE=Release -DAPP=S2SW -DMOM6SOLO=ON -DCCPP_SUITES=FV3_GFS_2017_coupled,FV3_GFS_v16_coupled ..
make -j 20
cd /scratch1/NCEPDEV/stmp2/Mark.Potts/cpld_bmark_wave_v16
rm PET* *.log ESMF*
export jobnum=`sbatch job_card  | awk -F" " '{print $4}'`
cd /scratch1/NCEPDEV/stmp2/Mark.Potts/ufs-test-artifacts
python3 ./python_scripts/archive_results.py -y config/ufs-hera.yaml -j $jobnum -t $tag




