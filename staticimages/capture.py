#!/usr/bin/python
# vim:set sw=4 ts=4 ai et:

import urllib
import time
import sys

# from ../server/webserver.py
def i_to_s_bits(i):
    s = ""
    for x in range(8):
        j = i & 1
        i = i / 2
        s = repr(j) + s
    return s

def set(i):
    print "Setting %d (%02X)" % (i, i)
    urllib.urlopen("http://lights.noisebridge.net:8080/run_one?delay=1000&seq=%02X" % i)

def confirm(i):
    print "Verifying %d" % i
    f = urllib.urlopen("http://lights.noisebridge.net:8080/active")
    lines = f.readlines()
    expected = i_to_s_bits(i) + "\n"
    if len(lines) != 2 or lines[0] != "1000\n" or lines[1] != expected:
        raise "The active file does not look correct?  Contents:" + lines

def save_image(outputdir, i):
    filename = "%s/image%02X.jpg" % (outputdir, i)
    print "Saving %s" % filename
    image = urllib.urlopen("http://lights.noisebridge.net:9190/singleframe/")
    output = open(filename, "w")
    output.write(image.read())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <output-directory>" % sys.argv[0]
        sys.exit(1)
    else:
        outputdir = sys.argv[1]

    for i in xrange(256):
        set(i)
        time.sleep(2)
        confirm(i)
        save_image(outputdir, i)
        confirm(i)
        print
