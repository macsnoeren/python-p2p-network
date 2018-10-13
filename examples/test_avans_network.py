#!/usr/bin/env python

#######################################################################################################################
# AVANS - BLOCKCHAIN - MINOR MAD                                                                                      #
#                                                                                                                     #
# Author: Maurice Snoeren                                                                                             #
# Version: 0.1 beta (use at your own risk)                                                                            #
#                                                                                                                     #
# Example python script to show the working principle of the TcpServerNode Node class.                                #
#######################################################################################################################

import time
import sys

sys.path.insert(0, '../src') # Import the files where the modules are located

from AvansNode import AvansNode

node1 = AvansNode('92.222.168.248', 10000)
node2 = AvansNode('92.222.168.248', 20000)
node3 = AvansNode('92.222.168.248', 30000)
node4 = AvansNode('92.222.168.248', 40000)
node5 = AvansNode('92.222.168.248', 50000)

node1.enable_visuals()
node2.enable_visuals()
node3.enable_visuals()
node4.enable_visuals()
node5.enable_visuals()

node1.start()
node2.start()
node3.start()
node4.start()
node5.start()

time.sleep(1)

node2.connect_with_node('92.222.168.248', 10000)
node3.connect_with_node('92.222.168.248', 10000)
node4.connect_with_node('92.222.168.248', 10000)
node5.connect_with_node('92.222.168.248', 20000)

time.sleep(5)

print("Network started.")


running = True
while running:
    print("Commands: connect, ping, discovery, stop")
    s = raw_input("Please type a command:") # python 2.x
    if ( s == "stop" ):
        running = False

    if ( s == "connect"):
        host = raw_input("host: ")
        port = int(raw_input("port: "))
        node1.connect_with_node(host, port)

    elif ( s == "ping" ):
        node1.send_ping()

    elif ( s == "discovery" ):
        node1.send_discovery()

    else:
        print("Command not understood '" + s + "'")            

print("main stopped")

node1.stop()
node2.stop()
node3.stop()
node4.stop()
node5.stop()

