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
import random

sys.path.insert(0, '../p2pnet') # Import the files where the modules are located

from AvansNode import AvansNode

total_nodes = 10

if ( len(sys.argv) > 1 ):
    total_nodes = int( sys.argv[1] )

if ( total_nodes < 1 ):
    total_nodes = 5

print("Creating a network with " + str(total_nodes))

nodes = []

basePort = 20000

print("Creating the network")
for i in range(total_nodes):
    node = AvansNode('localhost', basePort + i*100)
    nodes.append(node)
    del node
    
print("Enable visuals")
for i in range(total_nodes):
    nodes[i].enable_visuals()
    #nodes[i].enable_debug()

time.sleep(1)

print("Starting the nodes")
for i in range(total_nodes):
    nodes[i].start()

time.sleep(1)

print("Making the connections!")
for i in range(total_nodes):
    print("Creating connection " + str(i))
    nodes[i].connect_with_node('localhost', basePort + random.randint(1, total_nodes/5)*100)
    #time.sleep(1)

print("Network started.")

running = True
nodeIndex = 0
while running:
    print("Commands: node, connect, ping, discovery, stop")
    s = raw_input("Please type a command:") # python 2.x
    if ( s == "stop" ):
        running = False

    if ( s == "connect"):
        host = raw_input("host: ")
        port = int(raw_input("port: "))
        nodes[nodeIndex].connect_with_node(host, port)

    elif ( s == "ping" ):
        nodes[nodeIndex].send_ping()

    elif ( s == "discovery" ):
        nodes[nodeIndex].send_discovery()

    elif ( s == "node" ):
        nodeIndex = int(raw_input("node port")) - 10000
        print("Node selected: " + str(nodeIndex))

    else:
        print("Command not understood '" + s + "'")
            

print("main stopped")

for i in range(total_nodes):
    nodes[i].stop()

