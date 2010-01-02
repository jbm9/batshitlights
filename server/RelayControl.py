import sys
import ConfigParser
import logging

# This is for the Quasar 3108:
#  http://www.quasarelectronics.com/3108-8-channel-serial-relay-controller-isolated-io-board.htm
# datasheet/reference:
#   http://www.quasarelectronics.com/kit-files/electronic-kit/3108v3.pdf

rclog = logging.getLogger("serverlog.rc")


class RelayControl():
    def __init__(self, length=8):
        self.length = int(length)
        self.state = range(length)
        self.comerror = 0      # nonzero if com error
        for i in range(len(self.state)):
            self.state[i] = 0
        
    def status2str(self,status):
        str = ""
        mask = 1
        for i in range(8):
            if (status & (mask << i)):
                str += "1"
            else:
                str += "0"
        return(str)
    
    def set(self,channel,newstate):
        # top level set channel value command
        if(channel > self.length): return(0)
        if(channel < 0 ): return(0)
        self.setstate(channel,newstate)
        #return(self.setcontrol(channel,newstatus))
        return(1)

    def setstate(self,channel,state):
        rclog.debug("NULL set channel %d to %d" % (channel,state))
        return(0)
    
    def getstate(self,channel):
        rclog.debug("NULL PROC get status for channel %d" % channel)
        return
    

class SerialRelayControl(RelayControl):
    def __init__(self,length,cfg):
        RelayControl.__init__(self,length)
        import serial

        rclog.info("initializing serial relay control")
        self.ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
        
    def setstate(self,channel,status):
        if(status):
            outstr = "N"
        else:
            outstr = "F"
        outstr += "%1d\r" % (int(channel) + 1 )
        rclog.debug("SERIAL outstring = " + outstr)
        self.ser.write(outstr)    
        # and now eat up command echo
        response = self.ser.readline()
        rclog.debug("echo: " + response.strip())

    # status is an integer representing the 8b bitmask of relays
    def setstate_bulk(self, status):
        outstr = "R%02X\r"  % (status & 0xff)
        rclog.debug("SERIAL outstring = " + outstr)
        self.ser.write(outstr)    
        response = self.ser.readline()
        rclog.debug("echo: " + response.strip())

    def getstatus(self):
        self.ser.write("S0\r")
        response = self.ser.read(100)
        rclog.debug('status: "' + response + '"')
        rsplit = response.split("\r")
        if len(rsplit) > 2:
            if rsplit[0].strip() == "#S0":
               statint = int(rsplit[1].strip(), 16)
            else:
                statint = -1
        else:
            statint = -2
            rclog.debug("status: %X" % statint)

    def getcontrol(self,channel):
        outstr = "S%1d\r" % (int(channel) + 1 )
        #print "read channel " + outstr
        #self.ser.flush()
        self.ser.flushInput()
        self.ser.write(outstr)
        self.ser.flushOutput()
        # response is #SN \r 0/1 \r # = 6 chars
        response = self.ser.read(self.ser.inWaiting())
        #print '"' + response + '"'
        response = response.strip()
        if(len(response)):
            rclog.debug("response: '" + response + "'")
            if response[0] == '#':
               #status = int(response[3])
                status=0
            else:
                status = 1
        else:
            rclog.error("null response")
            status = 0
        return(status)    
               
    def close(self):
        self.ser.close()
        

