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


def callback_node_event1(event, node, other, data):
    print("Event Node 1 (" + node.id + "): %s: %s" % (event, data))
    node.send_to_nodes({"thank": "you"})


def callback_node_event2(event, node, other, data):
    print("Event Node 2 (" + node.id + "): %s: %s" % (event, data))
    node.send_to_nodes({"thank": "you"})


node1 = Node('localhost', 10000, callback_node_event1)
node2 = Node('localhost', 20000, callback_node_event2)

node1.start()
node2.start()

node1.connect_with_node('localhost', 20000)

#node1.terminate_flag.set()  # Stopping the thread

node1.send_to_nodes({"test": "ha", "ni": "hao"})

while True:
    time.sleep(1)

node1.stop()
node2.stop()

node1.join()
node2.join()

print("main stopped")

