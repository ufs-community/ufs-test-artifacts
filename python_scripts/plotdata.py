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
import matplotlib.pyplot as plt
import numpy as np




class PlotData:
  def __init__(self,args):

    self.machinename= args['machine']

    if(args['dryrun'] == "True"):
      self.dryrun = True
    else:
      self.dryrun = False
    timing = {} 
    print("dryrun is -- {}".format(self.dryrun))
    git_cmd = "git log --pretty=oneline | grep {}".format(self.machinename)
    output = self.runcmd(git_cmd)
    components = ['ATM','OCN','ICE','WAV']
    for line in output:
      words = line.split(" ")
      githash = words[0]
      versioncmd = "git show {}:{}/PET000.ESMF_LogFile | grep \"ESMF Version\"".format(githash,self.machinename)
      output = self.runcmd(versioncmd)
      words = output[0].split(": ")
      ESMFversion = words[1].split("'")[0]
      comptiming = {}
      for comp in components:
        cmd = "git show {}:{}/ESMF_Profile.summary | grep \"\[{}\] RunPhase1\"".format(githash,self.machinename,comp)
        output = self.runcmd(cmd)
        if(output != None):
          words = output[0].split()
#         print("{} {}".format(ESMFversion,words[4]))
          comptiming[comp] = words[4]
      if(comptiming != {}):
        cmd = "git show {}:{}/out | grep \"Total runtime\"".format(githash,self.machinename)
        output = self.runcmd(cmd)
        if(output != None ):
          runtime = output[0].split()[3]
          comptiming['runtime']=runtime
        timing[ESMFversion] = comptiming
    labels = timing.keys()
#   for key in timing:
#     if('runtime' in timing[key]):
#       print(key,timing[key]['runtime'])
    print(timing['ESMF_8_2_0_beta_snapshot_04']['ATM'])
#   men_means = [20, 34, 30, 35, 27]
#   women_means = [25, 32, 34, 20, 25]

#   x = np.arange(len(labels))  # the label locations
#   width = 0.35  # the width of the bars

#   fig, ax = plt.subplots()
#   rects1 = ax.bar(x - width/2, men_means, width, label='Men')
#   rects2 = ax.bar(x + width/2, women_means, width, label='Women')
    data = list(timing.items())
    an_array = np.array(data)
    print(an_array[0,1]['ATM'])
    print(labels)
    return


  def runcmd(self,cmd):
    if(self.dryrun == True):
       print("would have executed {}".format(cmd))
       output = None
    else:
      try:
        output = subprocess.check_output(cmd,shell=True).strip().decode('utf-8').splitlines()
      except:
        output = None
    return output



if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Plot changes over time in UFS coupled benchmarks')
  parser.add_argument('-m','--machine', help='name of machine used for plots', required=True)
  parser.add_argument('-d','--dryrun', help='dryrun (optional)', required=False,default=False)
  args = vars(parser.parse_args())
   
  plotter = PlotData(args)
    
