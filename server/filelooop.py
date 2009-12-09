import select
import os
import RelayControl
import time

rc = RelayControl.SerialRelayControl(length=8,cfg="")

def updatestate(rc, s):
    pos = 0
    for c in s:
        if pos < 8:
            # update state
            print "Update: " + repr(pos)+ " to " + c
            rc.setstate(pos, (c == "1"))
        pos = pos + 1

while True:
    f = open("/home/lights/sequence")
    globaldelay = int(f.readline())
    print "My globaldelay is " + repr(globaldelay)

    for line in f:
        tokens = line.strip().split()
        command = tokens[0]
        delay = len(tokens) > 1 and tokens or globaldelay
        updatestate(rc, line)
        time.sleep(delay/1000.0)

    #sys.exit(0)
