#!/usr/bin/python

import time

#print 'Healthcheck daemon starting now.......'

#while True:
#print "This prints once a minute."
import SimpleHTTPServer
import SocketServer

PORT = 8000

Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

print "serving at port", PORT
httpd.serve_forever()

#    time.sleep(5)  # Delay for 1 minute (60 seconds)	
