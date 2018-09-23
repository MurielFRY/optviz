#!/usr/bin/env python

from __future__ import print_function
import sys

filename = sys.argv[1]
f=open(filename, 'r')

joinorders=[]
fulljoinorder=[]
currentjoinorder=''
leadingtable=''
tablename=''

costsofar=0
prevcost=0
btaloc=0
bjoloc=0
sta={} # best single table access path costs (when 1st table in the join)
qb='' # keep track of the current query block we are in

for n, l in enumerate(f):
  l=l.strip()
  if l.startswith('Query Block SEL'): qb = l.split()[2]
  
  if l.startswith('Single Table Cardinality Estimation for'):
    tablename=l.split()[5]

  if l.startswith('Best:: AccessPath:'):
    btaloc = n

  #  Best:: AccessPath: TableScan
  #        Cost: 282927.639643  Degree: 1  Resp: 282927.639643  Card: 147287590.000000  Bytes: 0.000000
  #  make sure that we only take the Cost: if it's immediately after the best access path
  if l.startswith('Cost:') and n==btaloc+1:
    sta[tablename]=float(l.split()[1])

  if l.startswith('Join order['):
    fulljoinorder=[] 
    for s in l.split()[2:]:
      fulljoinorder.append(s.split('[')[0])

    joinorders.append(qb + " " + l)
    leadingtable = l.split()[2].split("#")[0]
    currentjoinorder=leadingtable
    costsofar=sta.get(leadingtable)
    #print("\n======" ,l)
    #print("%20s: %s: %s" % (sta.get(leadingtable), qb, leadingtable))
    print("%s %s: %s %s" % (qb, '->'.join(fulljoinorder), leadingtable, costsofar))

  if l.startswith('Now joining:'):
    tablename=l.split()[2].split("#")[0]
    currentjoinorder += ";" + tablename

  if l.startswith('Best:: JoinMethod:'):
      bjoloc = n

  if l.startswith('Cost:') and n==bjoloc+1:
    prevcost=costsofar    
    costsofar = float(l.split()[1])
    #print("%20s: %s: %s" % (costsofar, qb, currentjoinorder))
    print("%s %s: %s: %s" % (qb, '->'.join(fulljoinorder), currentjoinorder, costsofar-prevcost))

  
#for l in joinorders: print(l)
