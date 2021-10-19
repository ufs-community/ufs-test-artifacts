#!/bin/bash

set -eux

# Set Installed HPC-stack parameters
INSTALLED_HPC_STACK_PATH=$1
INSTALLED_HPC_STACK_VERSION=1.1.0

# Set installation path
PREFIX=$2

# Set source of hpc-stack repository
HPC_STACK_ROOT=$3

# Set the name of the yaml file to use for ESMF, MAPL, etc.
yaml=$HPC_STACK_ROOT/stack/stack_noaa.yaml

##########################
# USER NEED NOT EDIT BELOW
##########################
set +x
export MODULES=true
export HPC_STACK_ROOT
export PREFIX
echo $HPC_STACK_ROOT/config/config_$4.sh
source $HPC_STACK_ROOT/config/config_$4.sh
source $HPC_STACK_ROOT/stack_helpers.sh
if [[ -e $yaml ]]; then
  eval $(parse_yaml $yaml "STACK_")
else
  echo "ERROR: YAML FILE $yaml DOES NOT EXIST, ABORT!"
  exit 1
fi

# Initialize installed hpc-stack path
source $MODULESHOME/init/bash
module use $INSTALLED_HPC_STACK_PATH
module load hpc/$INSTALLED_HPC_STACK_VERSION
set -x

# Instructions from build_stack.sh need to be replicated
[[ $USE_SUDO =~ [yYtT] ]] && export SUDO="sudo" || export SUDO=""

# Make sure pkg/ dir is present
mkdir -p $HPC_STACK_ROOT/pkg

# Build and install
$HPC_STACK_ROOT/libs/build_esmf.sh
