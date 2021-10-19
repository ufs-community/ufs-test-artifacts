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
import git
from scheduler import scheduler
from noscheduler import NoScheduler
from pbs import pbs
from slurm import slurm




class RunTests:
  def __init__(self,args):
    self.root_path = pathlib.Path(__file__).parent.absolute()
    self.yaml=args['yaml']
    with open(args['yaml']) as file:
      yaml_list = yaml.load(file, Loader=yaml.FullLoader)
      self.machine_name = yaml_list['hostname']
      self.modulesdir= yaml_list['modulelocation']
      self.artifacts_root = yaml_list['artifactsdir']
      self.ufsdir = yaml_list['ufsdir']
      self.scriptdir= yaml_list['scriptdir']
      self.esmfdir= yaml_list['esmfdir']
      self.hpcstackdir= yaml_list['hpcstackdir']
      self.systemhpcstack= yaml_list['systemhpcstackdir']
      if(yaml_list['artifactname']):
        self.artifactname=yaml_list['artifactname'];
      else:
        self.artifactname="default"
    self.tags = []
    if(args['tag'] == None):
      self.getNewTags()
    else:
      self.tags.append(args['tag'])
   
    self.buildESMF()
    os.chdir(self.ufsdir)
    os.system("rm -rf ufs-weather-model")
    os.system("git clone --recurse-submodules https://github.com/ufs-community/ufs-weather-model.git")
    os.system("sed -i 's/module load esmf/#module load esmf/g' modulefiles/ufs_common")
    os.system("sed -i '/OMP_NUM_THREADS/a export ESMF_RUNTIME_PROFILE=ON\\nexport ESMF_RUNTIME_PROFILE_OUTPUT=\"SUMMARY BINARY\"' tests/fv3_conf/fv3_slurm.IN_{}".format(self.machine_name))
    self.genRTconf()
    for tag in self.tags:
      esmfmkfile = subprocess.check_output("find {} -iname esmf.mk | /usr/bin/grep {}".format(self.modulesdir,tag),shell=True).strip().decode('utf-8')
      os.system("echo \"setenv ESMFMKFILE {}\" >> modulefiles/ufs_common".format(esmfmkfile))
      print("root path is {}".format(self.root_path))
      os.chdir("tests")
      os.system("./rt.sh -k -l rt.prof")  
      rundir_root = subprocess.check_output("grep '+ RUNDIR_ROOT' log_{}.intel/* | head -n 1 | awk -F '=' '{{print $2}}'".format(self.machine_name),shell=True).strip().decode('utf-8')
      for testname in yaml_list['testnames']:
        jobid = subprocess.check_output("grep -Ri jobid log_{}.intel/run_{}.log | head -n 1 | awk -F ' ' '{{print $11}}'".format(self.machine_name,yaml_list['testnames'][testname]),shell=True).strip().decode('utf-8')
        print("jobid is {}".format(jobid))
        os.system("python3 {}/archive_results.py -y {} -j {} -t {} -D {}/{} -T {}".format(self.root_path,self.yaml,jobid,tag,rundir_root,yaml_list['testnames'][testname],yaml_list['testnames'][testname])) 
      os.system("sed -i '$ d' ../modulefiles/ufs_common")

  def buildESMF(self):
    for tag in self.tags:
      os.chdir(self.hpcstackdir)
      os.system("echo $PWD")
      os.system("module use {}".format(self.systemhpcstack));
      print("cp stack/stack_esmf_template.yaml stack/stack_noaa.yaml");
      os.system("cp stack/stack_esmf_template.yaml stack/stack_noaa.yaml");
      print("sed -i 's/ESMFTAG/{}/g' stack/stack_noaa.yaml".format(tag.replace("ESMF_","")));
      os.system("sed -i 's/ESMFTAG/{}/g' stack/stack_noaa.yaml".format(tag.replace("ESMF_","")));
      print("{}/build_standalone_esmf.sh {} {} {} {}".format(self.hpcstackdir,self.systemhpcstack,self.modulesdir,self.hpcstackdir,self.machine_name))
      os.system("{}/build_standalone_esmf.sh {} {} {} {}".format(self.hpcstackdir,self.systemhpcstack,self.modulesdir,self.hpcstackdir,self.machine_name))

  def getNewTags(self):
     repo = git.Repo(self.esmfdir)
     o = repo.remotes.origin
     o.pull()
     tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
     latest_tag = tags[-1]
     tagfile = open("{}/python_scripts/esmf-tags.txt".format(self.scriptdir),"r")
     old_tags = tagfile.readlines()
     tagfile.close()
     print("length of old and new tags is {} and {}".format(len(old_tags),len(tags)))
     if(len(old_tags) < len(tags)):
       #write out a new tag file
       tagfile = open("{}/python_scripts/esmf-tags.txt".format(self.scriptdir), "w")
       for tag in tags:
         tagfile.write("%s\n" % tag)
       for i in range(len(old_tags),len(tags)):
         print("{}".format(list(tags)[i]))
         self.tags.append(list(tags)[i])

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
  parser.add_argument('-t','--tag', help='tag for new test', required=False, default=None)
  args = vars(parser.parse_args())
   
  tester = RunTests(args)
    
