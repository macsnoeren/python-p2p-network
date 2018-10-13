#######################################################################################################################
# AVANS - BLOCKCHAIN - MINOR MAD                                                                                      #
#                                                                                                                     #
# Author: Maurice Snoeren                                                                                             #
# Version: 0.1 beta (use at your own risk)                                                                            #
#                                                                                                                     #
# Example python script to show the working principle of the TcpServerNode Node class.                                #
#######################################################################################################################

import time
import pprint
from TcpServerNode import Node

node1 = None
node2 = None

def callback_node_event(event, node, other, data):
    if ( event == "NODEINBOUNDCLOSED" ):
        print("NODE (" + node.getName() + "): " + event + "\n")

    elif ( event == "NODEOUTBOUNDCLOSED" ):
        print("NODE (" + node.getName() + "): " + event + "\n")

    elif ( event == "CONNECTEDWITHNODE" ):
        print("NODE (" + node.getName() + "): " + event + "\n")

    elif ( event == "NODECONNECTED" ):
        print("NODE (" + node.getName() + "): " + event + "\n")

    elif ( event == "NODEMESSAGE" ):
        print("NODE (" + node.getName() + "): " + event + ": " + str(data) + "\n")

    else:
        print("NODE (" + node.getName() + "): Event is not known " + event + "\n")

node1 = Node('localhost', 10000, callback_node_event)
node2 = Node('localhost', 20000, callback_node_event)
node3 = Node('localhost', 30000, callback_node_event)

node1.start()
node2.start()
node3.start()

node1.connect_with_node('localhost', 20000)
node3.connect_with_node('localhost', 10000)

time.sleep(2)

node1.send_to_nodes({"test": "ha", "ni": "hao"})

while True:
    node1.send_to_nodes({"node": "Node 1", "test": "ha", "ni": "hao"})
    time.sleep(1)

node1.stop()
node2.stop()
node3.stop()

node1.join()
node2.join()
node3.join()

print("main stopped")

