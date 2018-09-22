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
from AvansNode import AvansNode

node_p2p1 = AvansNode('localhost', 1000)
node_p2p2 = AvansNode('localhost', 2000)
node_p2p3 = AvansNode('localhost', 3000)
node_p2p4 = AvansNode('localhost', 4000)

node_p2p1.start()
node_p2p2.start()
node_p2p3.start()
node_p2p4.start()

# All nodes connect to node 1
node_p2p2.connect_with_node('localhost', 1000)
node_p2p3.connect_with_node('localhost', 1000)
node_p2p4.connect_with_node('localhost', 1000)

node_p2p1.print_connections()

time.sleep(5)

node_p2p1.send_to_nodes({"message": "Hoi daar"})

time.sleep(5)

node_p2p1.send_transacation("Maurice", "Diederich", 1000)


while True:
    time.sleep(1)

print("main stopped")

