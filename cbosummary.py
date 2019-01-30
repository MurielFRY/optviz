#!/usr/bin/env python

# Oracle Cost Based Optimizer summary generator (v0.1 alpha)
# Copyright 2018 Tanel Poder. All rights reserved. 
# More info at https://blog.tanelpoder.com

# TODO features
# 1) detect max cost and size the cost bar graph max width accordingly
# 2) add better support for multiple query blocks
# 3) HTMLize output

from __future__ import print_function
import sys, math

filename = sys.argv[1]
f=open(filename, 'r')

joinorders=[]
fulljoinorder=[]
joinorderid=0
currentjoinorder=''
leadingtable=''
tablename=''

costsofar=0
prevcost=0
bailedoutcost=0
btaloc=0
bjoloc=0
sta={} # best single table access path costs (when 1st table in the join)
qb='' # keep track of the current query block we are in

costs=[]

# join types in Oracle 18
# Hash
# HashSemi
# HashAnti
# HashNullAwareAnti
# HashSSNullAwareAnti
# HashFullOuterJoin
# HashNullAcceptingSemi
# SortMerge
# SortMergeSemi
# SortMergeAnti
# SortMergeNullAwareAnti
# SortMergeSSNullAwareAnti
# SortMergeNullAcceptingSemi
# NestedLoop
# NestedLoopSemi
# NestedLoopAnti
# NestedLoopSSNullAwareAnti
# NestedLoopNullAcceptingSemi
# NestedLoopGOJ
# SortMergeGOJ
# HashGOJ
# CubeSemi
# CubeAnti
# CubeSSNullAwareAnti


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
  #  or if an index scan then 2 lines down:
  #    Best:: AccessPath: IndexRange
  #    Index: STORE_SALES_IDX2
  #           Cost: 4.000750  Degree: 1  Resp: 4.000750  Card: 3.151835  Bytes: 0.000000
  #
  if l.startswith('Cost:') and n==btaloc+1:   # table
    sta[tablename]=float(l.split()[1])
  elif l.startswith('Cost:') and n==btaloc+2: # index
    sta[tablename]=float(l.split()[1])
  # TODO get the index name from previous line too


  if l.startswith('Join order['):
    print()
    prevcost=0
    joinorderid=int(l.split(']')[0].split('[')[1])
    fulljoinorder=[]
    for s in l.split()[2:]:
      #print('tanel: join order: ' + s)
      fulljoinorder.append(s.split('[')[0])

    joinorders.append(qb + " " + l)
    leadingtable = l.split()[2].split("#")[0]
    currentjoinorder="%s - %s" % (joinorderid, leadingtable)
    costsofar=sta.get(leadingtable, -1)
    if costsofar == -1: 
      #print("warning: costsofar for leading table %s = -1: possibly a query block is driving" % leadingtable)
      costsofar=0
    #print("\n======" ,l)
    #print("tanel: leadingtable: %s: %s: %s" % (sta.get(leadingtable), qb, leadingtable))
    #print("%s %s: %s %s" % (qb, '->'.join(fulljoinorder), leadingtable, costsofar))
    print("|%-30s| %8s+ | %-20s | %-20s | %s: %s" % ('#' * int(round(math.log(costsofar,2))), n, costsofar, qb, currentjoinorder, costsofar-prevcost))

  if l.startswith('Now joining:'):
    tablename=l.split()[2].split("#")[0]
    #currentjoinorder += ";%s - %s" % (joinorderid, tablename)
    currentjoinorder += ";" + tablename

  # record intermediate cost in case CBO bails out evaluating a join order early 
  # as its cost is already higher than a previously discovered best cost
  if l.startswith('Best NL cost:') or l.startswith('SM cost:') or l.startswith('HA cost:'):
    bailedoutcost=float(l.split(':')[1].strip())

  # CBO found a best join order so far
  if l.startswith('Best:: JoinMethod:'):
    bjotype = l.split()[2]
    currentjoinorder += "(%s)" % bjotype
    bjoloc  = n

  if l.startswith('Cost:') and n==bjoloc+1:
    prevcost=costsofar    
    costsofar = float(l.split()[1])
    print("|%-30s| %8s+ | %-20s | %-20s | %s: %s" % ('#' * int(round(math.log(costsofar,2))), n, costsofar, qb, currentjoinorder, costsofar-prevcost))
 
  if l.startswith('Join order aborted: cost > best plan cost'):
    prevcost=costsofar
    # intentionally not changing costsofar as we bailed out from this plan
    print("|%-30s| %8s- | %-20s | %-20s | %s: %s" % ('#' * int(round(math.log(bailedoutcost,2))), n, bailedoutcost, qb, currentjoinorder, bailedoutcost-prevcost))

  if l.startswith('Final cost for query block'):
    print('\n' + l)

  if l.startswith('Best join order:'):
    print(l + '\n')

#for l in joinorders: print(l)
