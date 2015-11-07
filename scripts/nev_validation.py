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

  # find events from total events from all flists pertaining to this dataset
  nflist = 0
  infiles_flist = {} # save input file list, in case we want to comb through it later
  for flistnm in flists:
    if ds in flistnm:
      for line in open(flistnm).readlines():
        if "/store" in line:
          filename = line.split("/store").pop().split()[0].strip()
          infiles_flist[filename] = int(line.split().pop(1))
        elif "nEventsTotal" in line:
          nflist = nflist + int(line.strip("nEventsTotal:"))

  # check the babies provenance for total number of events for all babies pertaining to this dataset
  nbaby = 0
  if ("Lept" in ds):
    # for datasets skimmed on-the-fly we have to add up the events 
    # we had ran over for each file; this is stored in treeglobal->Scan("nev_file")
    for roonm in glob.glob(babypath+"/*"+ds+"*root"):
      roof = TFile(roonm)
      for entry in roof.treeglobal:
        nbaby = nbaby + entry.nev_file
  else: 
    # for all others we can just do GetEntries on all the files together
    ch = TChain("tree")
    ch.Add(babypath+"/*"+ds+"*root")
    nbaby = ch.GetEntries()

  # does the number of events match?
  if (nbaby!=nflist):
    print "--------- FOUND MISMATCH ---------"
    print "flists N = ", nflist
    print "babies N = ", nbaby, "("+str(float(nbaby)/float(nflist)*100.), "%)"
    
    # find if all events in inputfiles were analyzed for each baby
    # i.e. compare provenance nev_file to what the flist says the total events should be 
    # for this baby's set of input files
    infiles_baby = []
    for babyname in glob.glob(babypath+"/*"+ds+"*root"):
      roof = TFile(babyname)
      for entry in roof.treeglobal:
        inputs = [ifl.split("/store").pop() for ifl in list(entry.inputfiles)]
        infiles_baby.extend(inputs)
        nev_das = 0
        for infile in inputs:
          if infile in infiles_flist.keys():
            nev_das = nev_das + infiles_flist[infile]
          else:
            print "File in baby inputfiles list, but not in flist:", infile
        if nev_das != entry.nev_file:
          print "Baby has %i, but should have %i events:" % (entry.nev_file,nev_das)
          print babyname

    # print differences in input file list in babies and das
    setflist = set(infiles_flist.keys())
    setbaby = set(infiles_baby)
    misses = setflist - setbaby
    extras = setbaby - setflist
    if misses:
      print "Missing input files:"
      for miss in misses: print miss
    if extras:
      print "Extra input files:" 
      for ex in extras: print ex
    print "----------------------------------"






