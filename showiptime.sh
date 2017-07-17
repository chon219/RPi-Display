#!/bin/bash

ip=`/sbin/ifconfig -a|grep inet|grep -v 127.0.0.1|grep -v inet6|awk '{print $2}'|tr -d "addr:"`
d=`/bin/date "+%a %b %d"`
t=`/bin/date "+%H:%M %Z %Y"`

/usr/local/bin/zerorpc "tcp://127.0.0.1:4242" displayText 0 2 1 "$d"
/usr/local/bin/zerorpc "tcp://127.0.0.1:4242" displayText 0 4 1 "$t"
/usr/local/bin/zerorpc "tcp://127.0.0.1:4242" displayText 0 6 1 "$ip"