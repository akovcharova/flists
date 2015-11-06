#! /usr/bin/env python
import os, sys 
import glob
import string, pprint
from ROOT import TFile, TH1D, TChain

babypath = "/net/cms2/cms2r0/babymaker/babies/2015_10_19/mc"
flistpath = "/net/cms2/cms2r0/babymaker/flists"

print
print "// Checking the events/dataset of MC production in", babypath
print "// against nEventsTotal reported in", flistpath
print

datasets = sorted(set([ifile.split("baby_").pop().split("_mf")[0] for ifile in glob.glob(babypath +"/*root")]))
flists = glob.glob(flistpath+"/*.txt")

for ds in datasets:
  print "Checking dataset:", ds
  nflist = 0
  for flistnm in flists:
    if ds in flistnm:
      line = open(flistnm).readlines()[-3]
      nflist = nflist + int(line.strip("nEventsTotal:"))
  nbaby = 0
  if ("Lept" in ds):
    for roonm in glob.glob(babypath+"/*"+ds+"*root"):
      roof = TFile(roonm)
      for event in roof.treeglobal:
        nbaby = nbaby + event.nev_file
  else:
    ch = TChain("tree")
    ch.Add(babypath+"/*"+ds+"*root")
    nbaby = ch.GetEntries()
  if (nbaby!=nflist):
    print "--------- FOUND MISMATCH"
    print "flists N = ", nflist
    print "babies N = ", nbaby
    