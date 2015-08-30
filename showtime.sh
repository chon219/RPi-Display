#!/bin/bash

/usr/local/bin/zerorpc "tcp://127.0.0.1:4242" displayString 0 0 4 ""

d=`/bin/date "+%A %b %d"`
t=`/bin/date "+%H:%M %Z %Y"`

/usr/local/bin/zerorpc "tcp://127.0.0.1:4242" displayString 0 2 1 "$d"
/usr/local/bin/zerorpc "tcp://127.0.0.1:4242" displayString 0 4 1 "$t"
