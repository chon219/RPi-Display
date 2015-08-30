#!/usr/bin/python

from display import Display
import zerorpc
import time

def main():
    try:
        disp = Display(15, 13, "/home/pi/wenquanyi_12pt.bdf")
        print "display ready"
        s = zerorpc.Server(disp)
        s.bind("tcp://0.0.0.0:4242")
        s.run()
    except Exception, e:
        print e

if __name__ == "__main__":
    main()
