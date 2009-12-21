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
    def base_path(self):
        return "/home/lights/batshitlights"
        # This doesn't work with the way we run on lights.nb.  Eh?
        # return os.path.abspath( os.path.dirname(__file__) + "/..")

    def params(self, s):
        d = dict( map(lambda s:s.split("=", 2), s.split("&")) )
        return d

    def handle_root(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()

        p = re.compile('\.seq$')

        files = [ p.sub('', f) for f in listdir(self.base_path() + "/sequences") if f.endswith(".seq") ]

        header = open(self.base_path() + "/html/header.html")
        self.wfile.write(header.read())
        header.close()

        for f in sorted(files):
            #self.wfile.write("<li><a href=/%s.seq>%s</a></li>\n" % (f,f) )
            #self.wfile.write("<li><a href='javascript:bgsend(\"%s\")'>%s</a></li>\n" % (f,f) )
            self.wfile.write("<li><a href='/sequences/%s.seq' onclick='bgsend(\"sequences/%s\");return false' rel=\"nofollow\">%s</a></li>\n" % (f, f,f) )

        footer = open(self.base_path() + "/html/footer.html")
        self.wfile.write(footer.read())
        footer.close()
        return

    def handle_seq(self):
        p = re.compile('sequences/')
        file = p.sub('', self.path)

        input = open(self.base_path() + "/sequences" + file)
        output = open(self.base_path() + "/sequences/active", "w")
        output.write(input.read())
        input.close()
        output.close()

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()

        displayhtml = open(self.base_path() + "/html/set.html")
        self.wfile.write(displayhtml.read())
        displayhtml.close()

        self.restart_fileloop()
        return

    def restart_fileloop(self):
        # Total kludge to restart fileloop.py, and get the new sequence
        # running faster.  Otherwise, we need to wait for the current
        # sequence to finish before it re-reads the file again.
        #os.system('kill -HUP $(cat /var/run/fileloop.py) &> /dev/null')
        os.system('sudo svc -t /etc/service/fileloop')
         

    def handle_active(self):
        input = open(self.base_path() + "/sequences/active")
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()
        self.wfile.write(input.read())
        input.close()

    def handle_png(self):
        png = open(self.base_path() + "/html/" + self.path)
        self.send_response(200)
        self.send_header('Content-type','image/png')
        self.send_header('Content-Length', os.fstat(png.fileno())[6])
        self.end_headers()
        self.wfile.write(png.read())
        png.close()
        return

    def handle_icon(self):
        icon = open(self.base_path() + "/html/" + self.path)
        self.send_response(200)
        self.send_header('Content-type','image/x-icon')
        self.send_header('Content-Length', os.fstat(icon.fileno())[6])
        self.end_headers()
        self.wfile.write(icon.read())
        icon.close()
        return

    def handle_txt(self):
        txt = open(self.base_path() + "/html/" + self.path)
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.send_header('Content-Length', os.fstat(txt.fileno())[6])
        self.end_headers()
        self.wfile.write(txt.read())
        txt.close()
        return

    def unpack_seq_string(self, s):
        pos = 0

        retval = []
        curval = 0

        for c in s:
            pos = (pos + 1) % 2
            curval = curval * 16
            curval = curval + int(c, 0x10)
            if pos == 0:
                retval.append(curval)
                curval = 0
        return retval

    def i_to_s_bits(self, i):
        s = ""

        for x in range(8):
            j = i & 1
            i = i / 2
            s = repr(j) + s
        return s

    def handle_run_one(self):
        params = self.params(self.parsed_path[4])
        self.log_message("params = " + repr(params))
        delay = params["delay"]
        seq_s = params["seq"]
        seq = self.unpack_seq_string(seq_s)
        self.log_message("seq = " + repr(map(self.i_to_s_bits,seq)))

        output = open(self.base_path() + "/sequences/active", "w")
        output.write(str(delay))
        output.write("\n")
        for s in seq:
            output.write(self.i_to_s_bits(s))
            output.write("\n")
        output.close
        self.restart_fileloop()

        self.handle_root()
        return

    def do_GET(self):
        try:
            self.parsed_path = urlparse(self.path)
            referer = self.headers.get('referer')
            self.log_message("referer: " + referer)

            requested_path = self.parsed_path[2]

            # Directory listing
            if requested_path == "/":
                return self.handle_root()

            # /run_one?delay=666&seq=0102ff 
            # anonymously adds a new sequence with the given delay and bitmasks
            if requested_path == "/run_one":
                return self.handle_run_one()

            # A request to set a specific sequence file
            if requested_path.endswith(".seq"):
                return self.handle_seq()

            # Print the current active sequence to the client
            if requested_path == "/active":
                return self.handle_active()
 
            if requested_path.endswith(".png"):
                return self.handle_png()

            if requested_path.endswith(".ico"):
                return self.handle_icon()

            if requested_path.endswith(".txt"):
                return self.handle_txt()

            self.send_error(404, "You're better off without that file.  Trust me.")

        #except IOError:
        except: 
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
