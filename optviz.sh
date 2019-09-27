#!/bin/bash

FNAME=`basename $1`

./cbosummary.py $1 | grep -v '^$' | awk -F'|' '{ print $6 }' | sed 's/^ //' | grep -v '^$' | \
  flamegraph.pl --countname=Cost --title=OptViz-$FNAME - > $FNAME.svg

open $FNAME.svg

