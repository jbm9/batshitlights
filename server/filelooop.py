# vim:set ts=4 sw=4 ai et:

import os
import RelayControl
import time

rc = RelayControl.SerialRelayControl(length=8,cfg="")

def updatestate(rc, s):
    pos = 0
    state = 0
    for c in s:
        if pos < 8:
            # update state
            print "Update: " + repr(pos)+ " to " + c
            state = 2*state
            if c == "1":
                state += 1

            # rc.setstate(pos, (c == "1"))
        pos = pos + 1

    print "Update: " + str(state)
    rc.setstate_bulk(state)

while True:
    f = open("/home/lights/batshitlights/sequences/active")
    globaldelay = int(f.readline())
    print "My globaldelay is " + repr(globaldelay)

    for line in f:
        tokens = line.strip().split()
        command = tokens[0]
        command = command[::-1]  # reverse the line.  don't ask.
        delay = len(tokens) > 1 and int(tokens[1]) or globaldelay
        updatestate(rc, command)
        if (delay < 50):
            delay = 50
        time.sleep(delay/1000.0)

    #sys.exit(0)
