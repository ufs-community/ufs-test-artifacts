import os
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
  def __init__(self,jobid,rundir,machine_name,scheduler,artifacts_root,dryrun):

    self.root_path = pathlib.Path(__file__).parent.absolute()
    self.jobid = jobid
    self.rundir = rundir
    self.machine_name = machine_name
    if(scheduler == "pbs"):
      self.scheduler=pbs("pbs")
    elif(scheduler == "slurm"):
      self.scheduler=slurm("slurm")
    elif(scheduler == "None"):
      self.scheduler=NoScheduler("slurm")
    self.artifacts_root = artifacts_root
    self.dryrun = dryrun
    print("dryrun is {} -- {}".format(dryrun,self.dryrun))
    start_time = time.time()
    seconds = 14400
    while True:
      current_time = time.time()
      elapsed_time = current_time - start_time
      job_done = self.scheduler.checkqueue(jobid)
      if(job_done):
        oe_filelist = glob.glob('{}/*log*'.format(rundir))
        oe_filelist.extend(glob.glob('{}/PET*'.format(rundir)))
        oe_filelist.extend(glob.glob('{}/out'.format(rundir)))
        oe_filelist.extend(glob.glob('{}/err'.format(rundir)))
        oe_filelist.extend(glob.glob('{}/nems*'.format(rundir)))
        oe_filelist.extend(glob.glob('{}/ESMF_Profile.summary'.format(rundir)))
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
    for cfile in oe_filelist:
      cp_cmd = 'cp {} .'.format(cfile)
      print("cp command is {}".format(cp_cmd))
      self.runcmd(cp_cmd)

    git_cmd = "git add *;git commit -a -m\'update for cpld_bmark run';git push origin main"
    self.runcmd(git_cmd)
    return


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='ESMF nightly build/test system')
  parser.add_argument('-j','--self.jobid', help='directory where builds will be mad #', required=True)
  parser.add_argument('-r','--rundir', help='directory where artifacts will be collected', required=True)
  parser.add_argument('-m','--machinename', help='name of machine where tests were run', required=False,default=False)
  parser.add_argument('-s','--scheduler', help='type of scheduler used', required=False,default=None)
  parser.add_argument('-a','--artifactsrootdir', help='directory where artifacts will be placed', required=True)
  parser.add_argument('-d','--dryrun', help='dryrun?', required=False,default=False)
  args = vars(parser.parse_args())
  
  archiver = ArchiveResults(args['self.jobid'],args['rundir'],args['machinename'],args['scheduler'],args['artifactsrootdir'],args['dryrun'])
    
