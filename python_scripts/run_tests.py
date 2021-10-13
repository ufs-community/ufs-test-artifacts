import os
import yaml
import subprocess
import argparse
import datetime
import sys
import time
import glob
import re
import pathlib
from shutil import copy2
from scheduler import scheduler
from noscheduler import NoScheduler
from pbs import pbs
from slurm import slurm




class RunTests:
  def __init__(self,args):
    self.tag=args['tag']
    with open(args['yaml']) as file:
      yaml_list = yaml.load(file, Loader=yaml.FullLoader)
      self.machine_name = yaml_list['hostname']
      self.modulesdir= yaml_list['modulelocation']
      self.artifacts_root = yaml_list['artifactsdir']
      self.ufsdir = yaml_list['ufsdir']
      self.scriptdir= yaml_list['scriptdir']
      if(yaml_list['artifactname']):
        self.artifactname=yaml_list['artifactname'];
      else:
        self.artifactname="default"
    os.chdir(self.ufsdir)
#   os.system("rm -rf ufs-weather-model")
#   os.system("git clone --recurse-submodules https://github.com/ufs-community/ufs-weather-model.git")
    os.system("sed -i 's/module load esmf/#module load esmf/g' modulefiles/ufs_common")
    os.system("sed -i '/OMP_NUM_THREADS/a export ESMF_RUNTIME_PROFILE=ON\\nexport ESMF_RUNTIME_PROFILE_OUTPUT=\"SUMMARY BINARY\"' tests/fv3_conf/fv3_slurm.IN_{}".format(self.machine_name))
    self.genRTconf()
    esmfmkfile = subprocess.check_output("find {} -iname esmf.mk | /usr/bin/grep {}".format(self.modulesdir,self.tag),shell=True).strip().decode('utf-8')
    os.system("echo \"setenv ESMFMKFILE {}\" >> modulefiles/ufs_common".format(esmfmkfile))
    self.root_path = pathlib.Path(__file__).parent.absolute()
    os.chdir("tests")
    os.system("./rt.sh -k -l rt.prof")  

  def genRTconf(self):
    rtconf = open('tests/rt.conf', 'r')
    rtprof = open('tests/rt.prof', 'w')
    Lines = rtconf.readlines()
    startwrite = False
    for line in Lines:
      s2sw = re.search("APP=S2SW", line)
      compileline = re.match("COMPILE", line)
      if s2sw:
        startwrite = True
      elif compileline:
        startwrite = False
      if startwrite == True:
        rtprof.writelines(line)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='ESMF nightly build/test system')
  parser.add_argument('-y','--yaml', help='Yaml file defining builds and testing parameters', required=True)
  parser.add_argument('-t','--tag', help='tag for new test', required=True)
  args = vars(parser.parse_args())
   
  tester = RunTests(args)
    
