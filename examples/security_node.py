#######################################################################################################################
# Author: Maurice Snoeren                                                                                             #
# Version: 0.1 beta (use at your own risk)                                                                            #
#                                                                                                                     #
# This example uses the SecurityNode to implement a security node and the functionality of this security node.        #
# As example all commands are from the commandline                                                                    #
# Commandline: python security_node.py <port>
#######################################################################################################################

import sys
import time
sys.path.insert(0, '..') # Import the files where the modules are located

from p2pnetwork.SecurityNode import SecurityNode

port = 9001
if len(sys.argv) > 1:
    print(sys.argv[1])
    port = int(sys.argv[1])

security_node = SecurityNode("127.0.0.1", port)

security_node.start()
#security_node.debug = True
time.sleep(1)

security_node.connect_with_node('vmacman.jmnl.nl', 15000)
time.sleep(2)

running = True
while running:
    print("Commands: message, ping, discovery, status, connect, stop")
    s = input("Please type a command:")
    if s == "stop":
        running = False

    elif s == "message":
        security_node.send_message("Hoi daar!")

    elif s == "ping":
        security_node.send_ping()

    elif s == "discovery":
        security_node.send_discovery()

    elif s == "status":
        security_node.print_connections()

    elif ( s == "connect"):
        host = input("host: ")
        port = int(input("port: "))
        security_node.connect_with_node(host, port)

    else:
        print("Command not understood '" + s + "'")   

security_node.stop()
