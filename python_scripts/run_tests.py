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
    os.chdir("ufs-weather-model")
    os.system("sed -i 's/module load esmf/#module load esmf/g' modulefiles/ufs_common")
    copy2(os.path.join(self.scriptdir, "config", "fv3_slurm.IN_{}".format(self.machine_name)), "tests/fv3_conf" )
    copy2(os.path.join(self.scriptdir, "config", "rt.prof".format(self.machine_name)), "tests" )
    esmfmkfile = subprocess.check_output("find {} -iname esmf.mk | /usr/bin/grep {}".format(self.modulesdir,self.tag),shell=True).strip().decode('utf-8')
    print("sed -i \'s/esmfmkfilepath/{}/g\' tests/rt.prof".format(esmfmkfile))
    os.system("sed -i 's/esmfmkfilepath/{}/g' tests/rt.prof".format(esmfmkfile))
    print("HEY esmfmkfile is {}".format(esmfmkfile))
    self.root_path = pathlib.Path(__file__).parent.absolute()
    if(args['dryrun'] == "True"):
      self.dryrun = True
    else:
      self.dryrun = False
    
    print("dryrun is -- {}".format(self.dryrun))

  def runcmd(self,cmd):
    if(self.dryrun == True):
       print("would have executed {}".format(cmd))
    else:
       os.system(cmd)
    return


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='ESMF nightly build/test system')
  parser.add_argument('-y','--yaml', help='Yaml file defining builds and testing parameters', required=True)
  parser.add_argument('-t','--tag', help='tag for new test', required=True)
  parser.add_argument('-d','--dryrun', help='directory where artifacts will be placed', required=False,default=False)
  args = vars(parser.parse_args())
   
  tester = RunTests(args)
    
