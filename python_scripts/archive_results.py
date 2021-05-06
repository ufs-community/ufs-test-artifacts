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
from scheduler import scheduler
from noscheduler import NoScheduler
from pbs import pbs
from slurm import slurm




class ArchiveResults:
  def __init__(self,args):

    self.jobid = args['jobid']

    with open(args['yaml']) as file:
      yaml_list = yaml.load(file, Loader=yaml.FullLoader)
      if self.jobid == "None":
        self.jobid = yaml_list['jobid']
      self.rundir = yaml_list['collectiondir']
      self.machine_name = yaml_list['hostname']
      scheduler = yaml_list['scheduler']
      print("HEY, scheduler is {}".format(scheduler))
      self.artifacts_root = yaml_list['artifactsdir']
      if(yaml_list['artifactname']):
        self.artifactname=yaml_list['artifactname'];
      else:
        self.artifactname="default"


    self.root_path = pathlib.Path(__file__).parent.absolute()
    if(scheduler == "pbs"):
      self.scheduler=pbs("pbs")
    elif(scheduler == "slurm"):
      self.scheduler=slurm("slurm")
    elif(scheduler == "None" ):
      print("creating no scheduler")
      self.scheduler=NoScheduler("None")
    else:
      print("bad scheduler type")
      return
    if(args['dryrun'] == "True"):
      self.dryrun = True
    else:
      self.dryrun = False
    
    print("dryrun is -- {}".format(self.dryrun))
    start_time = time.time()
    seconds = 14400
    while True:
      current_time = time.time()
      elapsed_time = current_time - start_time
      job_done = self.scheduler.checkqueue(self.jobid)
      if(job_done):
        oe_filelist = [];
        for key in yaml_list['collectedfiles']:
          regex = yaml_list['collectedfiles'][key]
          print("HEY, regex is {}/{}".format(self.rundir,regex))
          oe_filelist.extend(glob.glob('{}/{}'.format(self.rundir,regex)))
        print("filelist is {}".format(oe_filelist))
        print("oe list is {}\n".format(oe_filelist))
        self.copy_artifacts(oe_filelist)
        break
      time.sleep(30)

      if elapsed_time > seconds:
         print("Finished iterating in: " + str(int(elapsed_time))  + " seconds")
         break

  def runcmd(self,cmd):
    if(self.dryrun == True):
       print("would have executed {}".format(cmd))
    else:
       os.system(cmd)

  def copy_artifacts(self,oe_filelist):
  
    cwd = os.getcwd()
    os.chdir(self.artifacts_root)
    if(oe_filelist == []):
      return
    mkdir_cmd = "mkdir -p {}".format(self.machine_name)
    self.runcmd(mkdir_cmd)
    for cfile in oe_filelist:
      cp_cmd = 'cp {} ./{}'.format(cfile,self.machine_name)
      print("cp command is {}".format(cp_cmd))
      self.runcmd(cp_cmd)

    git_cmd = "git add *;git commit -a -m\'update for {} on {}';git push origin main".format(self.artifactname,self.machine_name)
    self.runcmd(git_cmd)
    return


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='ESMF nightly build/test system')
  parser.add_argument('-j','--jobid', help='directory where builds will be mad #', required=False,default="None")
  parser.add_argument('-y','--yaml', help='Yaml file defining builds and testing parameters', required=True)
  parser.add_argument('-d','--dryrun', help='directory where artifacts will be placed', required=False,default=False)
  args = vars(parser.parse_args())
   
  archiver = ArchiveResults(args)
    
