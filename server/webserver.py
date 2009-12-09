# Lights server: python-based webserver to handle Lights lab control

import string,cgi,time,sys
from os import curdir, sep, listdir
from urlparse import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import signal
#from RelayControl import RelayControl, ComtrolRelayControl
#from RelayControl import RelayControl, SerialRelayControl
import ConfigParser
import logging, logging.config

class LightsHandler(BaseHTTPRequestHandler):

    def create_button(self,index,value):
        button = "<hr><form method='GET' action='http://127.0.0.1:8080/action'" 

        button += " TARGET=_SELF>"
        button += "<input type='submit' name='coil%1d' value='1'>" % index

        if(value=="1"):
            button += "<span style='background-color:#81F781'>"
            button += " device %1d ON </span>" % index 
        else:
            button += "<span style='background-color:#F78181'>"
            button += "device %1d OFF </span>" % index         

        button += "<input type='submit' name='coil%1d' value='0'>" % index
        button += "</form>"
        return(button)

    def logtodb(self,channel,value):
        pass
    
    def create_return_page(self,status):
        f = open(curdir + "/activeheader.html") 
        page = f.read()
        f.close()
        self.server.log.info("Creating button page with status:" + status)
        page += "<body>"
        page +="Status is " + str(status)
        for i in range(0,8):
            page += self.create_button(i,status[i])
            page += "</body></html>"
        return(page)

    def path2channel(self):
        """ extract channel X and value Y from 'coilX=Y' url arg"""
        arg = self.parsed_path[4]
        channel = int(arg[4])
        value = int(arg[-1])
        return(channel,value)


    def do_GET(self):
        try:
            self.parsed_path = urlparse(self.path)
            if self.path.endswith(".seq"):
                #f = open(curdir + sep + self.path) #self.path has /test.html
                #f = open("/home/lights" + self.parsed_path[-1])
                input = open("/home/lights" + self.path)
                output = open("/home/lights/sequence", "w")

                output.write(input.read())

                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()

                #input.seek(0, 0)
                #self.wfile.write(input.read())

                displayhtml = open("/home/lights/set.html")
                self.wfile.write(displayhtml.read())

                input.close()
                output.close()

            if self.parsed_path[2] == "/":
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()

                #self.wfile.write("Files:")
                files = [ f for f in listdir("/home/lights") if f.endswith(".seq") ]
                #self.wfile.write(repr(files))

                for f in files:
                    self.wfile.write("<li><a href=/%s>%s</a><p>" % (f,f) )

            if self.path.endswith(".html"):
                f = open(curdir + sep + self.path) #self.path has /test.html
#note that this potentially makes every file on your computer readable by the internet

                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return
            if self.parsed_path[2] == "/action":
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.send_header('viewport',"content='width=320; initial-scale=1.0; maximum-scale=1.0; user-scalable=0;'/>")

                self.end_headers()
                (channel, val) = self.path2channel()
                self.server.log.info("Setting chan: %d to %d" %(channel,val))
                #self.server.RC.set(channel,val)
                #
                #statusstr = self.server.RC.getstate()
                statusstr="11111111"
                if statusstr == "error":
                    self.wfile.write("<body>waiting... refresh</body></html>")
                else:
                    self.wfile.write(self.create_return_page(statusstr))
                self.wfile.close()
                return

            return
 
        #except: 
            #raise
        except IOError:
            self.send_error(400,'Something bad happened: %s' % self.path)
            raise

    def do_POST(self):
        self.do_GET(self)
        return

        global rootnode
        try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                query=cgi.parse_multipart(self.rfile, pdict)
            self.send_response(301)
            
            self.end_headers()
            #print query
            #print pdict
            #sys.stdout.flush() 
            #upfilecontent = query.get('upfile')
            #print "filecontent", upfilecontent[0]
            #self.wfile.write("<HTML>POST OK.<BR><BR>");
            #self.wfile.write(upfilecontent[0]);
            
        except :
            raise



def main():
    # Make Ctrl+Break raise KeyboardInterrupt, like Python's default Ctrl+C
    # (SIGINT) behavior.

    # first read config file to figure out what we are doing
    cfgfile = "webserver.conf"
    cfg = ConfigParser.RawConfigParser()
    logging.config.fileConfig(cfgfile)
    
    try:  
        cfg.readfp(open(cfgfile))
    except:
        print "Error: can't find omega configuration file %s" % cfgfile
        exit(-1)

    port = cfg.getint("main", "server_port")

    #myRC = SerialRelayControl(length=8)
    #myRC = SocketRelayControl(length=8,cfg=cfg)
    #myRC = SerialRelayControl(length=8,cfg=cfg)

    # create logger (using config file for config)
    svrlog = logging.getLogger('serverlog')

    try:
        server = HTTPServer(('', port), LightsHandler)
        server.log = svrlog
        server.log.info("Running on port %d and ready to serve!" % port)
        #server.RC = myRC
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()

