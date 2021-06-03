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
import matplotlib



class PlotData:
  def __init__(self,args):

    self.machinename= args['machine']

    if(args['dryrun'] == "True"):
      self.dryrun = True
    else:
      self.dryrun = False
    
    print("dryrun is -- {}".format(self.dryrun))
    git_cmd = "git log --pretty=oneline | grep {}".format(self.machinename)
    output = self.runcmd(git_cmd)
    print("output is {}".format(output))
    return


  def runcmd(self,cmd):
    if(self.dryrun == True):
       print("would have executed {}".format(cmd))
       output = None
    else:
       output = subprocess.check_output(cmd,shell=True).strip().decode('utf-8')
    return output



if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Plot changes over time in UFS coupled benchmarks')
  parser.add_argument('-m','--machine', help='name of machine used for plots', required=True)
  parser.add_argument('-d','--dryrun', help='dryrun (optional)', required=False,default=False)
  args = vars(parser.parse_args())
   
  plotter = PlotData(args)
    
