# vim:set ts=4 sw=4 ai et:
# Lights server: python-based webserver to handle Lights lab control

import string,cgi,time,sys
from os import curdir, sep, listdir
import os
from urlparse import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import signal
import ConfigParser
import logging, logging.config
import re

class LightsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            self.parsed_path = urlparse(self.path)

            # Directory listing
            if self.parsed_path[2] == "/":
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()

                p = re.compile('\.seq$')
                p.sub('', "foo.seq")

                files = [ p.sub('', f) for f in listdir("/home/lights/batshitlights/sequences") if f.endswith(".seq") ]

                header = open("/home/lights/batshitlights/html/header.html")
                self.wfile.write(header.read())
                header.close()

                for f in sorted(files):
                    self.wfile.write("<li><a href=/%s.seq>%s</a></li>\n" % (f,f) )

                footer = open("/home/lights/batshitlights/html/footer.html")
                self.wfile.write(footer.read())
                footer.close()
                return

            # A request to set a specific sequence file
            if self.path.endswith(".seq"):
                input = open("/home/lights/batshitlights/sequences" + self.path)
                output = open("/home/lights/batshitlights/sequences/active", "w")
                output.write(input.read())
                input.close()
                output.close()

                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()

                displayhtml = open("/home/lights/batshitlights/html/set.html")
                self.wfile.write(displayhtml.read())
                displayhtml.close()

                # Total kludge to restart fileloop.py, and get the new sequence
                # running faster.  Otherwise, we need to wait for the current
                # sequence to finish before it re-reads the file again.
                #os.system('kill -HUP $(cat /var/run/fileloop.py) &> /dev/null')
                os.system('sudo svc -t /etc/service/fileloop')
                return
 
            # A request to set a specific sequence file
            if self.path.endswith(".png"):
                png = open("/home/lights/batshitlights/html/" + self.path)
                self.send_response(200)
                self.send_header('Content-type','image/png')
                self.send_header('Content-Length', os.fstat(png.fileno())[6])
                self.end_headers()
                self.wfile.write(png.read())
                png.close()
                return
        #except: 
        except IOError:
            self.send_error(400,'Something bad happened: %s' % self.path)
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

    # create logger (using config file for config)
    svrlog = logging.getLogger('serverlog')

    try:
        server = HTTPServer(('', port), LightsHandler)
        server.log = svrlog
        server.log.info("Running on port %d and ready to serve!" % port)
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()
