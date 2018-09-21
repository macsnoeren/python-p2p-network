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
        print("NODE: " + event + "\n")

    elif ( event == "NODEOUTBOUNDCLOSED" ):
        print("NODE: " + event + "\n")

    elif ( event == "CONNECTEDWITHNODE" ):
        print("NODE: " + event + "\n")

    elif ( event == "NODECONNECTED" ):
        print("NODE: " + event + "\n")

    elif ( event == "NODEMESSAGE" ):
        print("NODE: " + event + ": " + str(data) + "\n")

    else:
        print("NODE: Event is not known: " + event)

node1 = Node('localhost', 10000, callback_node_event)
node2 = Node('localhost', 20000, callback_node_event)

node1.start()
node2.start()

node1.connect_with_node('localhost', 20000)

time.sleep(2)

#node1.terminate_flag.set()  # Stopping the thread

node1.send_to_nodes({"test": "ha", "ni": "hao"})

while True:
    node1.send_to_nodes({"node": "Node 1", "test": "ha", "ni": "hao"})
    node2.send_to_nodes({"node": "Node 2", "test": "ha", "ni": "hao"})
    time.sleep(1)

node1.stop()
node2.stop()

node1.join()
node2.join()

print("main stopped")

