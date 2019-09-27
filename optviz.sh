#!/bin/bash

FNAME=`basename $1`

./cbosummary.py $1 | grep -v '^$' | awk -F'|' '{ print $4 " " $6 }' | grep -v '^ *$' | awk '{ print $2 ";" $4 " " $1 }' | \
  flamegraph.pl --countname=Cost --title=OptViz-$FNAME - > $FNAME.svg

open $FNAME.svg

