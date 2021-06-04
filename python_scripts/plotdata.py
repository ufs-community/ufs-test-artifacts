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
        else:
          comptiming[comp] = 0.0
      if(comptiming != {}):
        cmd = "git show {}:{}/out | grep \"Total runtime\"".format(githash,self.machinename)
        output = self.runcmd(cmd)
        if(output != None ):
          runtime = output[0].split()[3]
          comptiming['runtime']=runtime
        if ESMFversion in timing.keys():
          pass
        else:
          timing[ESMFversion] = comptiming
    labels = sorted(timing.keys())
    print(labels)
    labels = [w.replace('ESMF_', '') for w in labels]
    labels = [w.replace('beta_snapshot_', '') for w in labels]

    x = np.arange(len(labels))  # the label locations
    width = 0.175  # the width of the bars
    atm = np.zeros(len(timing))
    ocn = np.zeros(len(timing))
    ice = np.zeros(len(timing))
    wav = np.zeros(len(timing))
    i = 0
    for key in sorted (timing.keys()):
      atm[i] = timing[key]['ATM']
      ocn[i] = timing[key]['OCN']
      ice[i] = timing[key]['ICE']
      wav[i] = timing[key]['WAV']
      i = i +1

    fig, ax = plt.subplots(figsize=(12,4))
    rects1 = ax.bar(x - width*1.5, atm, width, label='ATM')
    rects2 = ax.bar(x - width*0.5, ocn, width, label='OCN')
    rects3 = ax.bar(x + width*0.5, ice, width, label='ICE')
    rects4 = ax.bar(x + width*1.5, wav, width, label='WAV')

    ax.set_ylabel('Time (seconds)')
    ax.set_title('Component Timing by ESMF snapshot on {}'.format(self.machinename))
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)
    ax.bar_label(rects3, padding=3)
    ax.bar_label(rects4, padding=3)

    fig.tight_layout()

    plt.savefig('{}-comp-timing.png'.format(self.machinename))
    plt.show()
    print(atm)
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
    
