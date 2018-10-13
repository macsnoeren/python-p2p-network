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
from MyPeer2PeerNode import MyPeer2PeerNode

node_p2p1 = MyPeer2PeerNode('localhost', 1000)
node_p2p2 = MyPeer2PeerNode('localhost', 2000)
node_p2p3 = MyPeer2PeerNode('localhost', 3000)
node_p2p4 = MyPeer2PeerNode('localhost', 4000)

node_p2p1.start()
node_p2p2.start()
node_p2p3.start()
node_p2p4.start()

# All nodes connect to node 1
node_p2p2.connect_with_node('localhost', 1000)
node_p2p3.connect_with_node('localhost', 1000)
node_p2p4.connect_with_node('localhost', 1000)

node_p2p1.send_to_nodes({"message": "Hoi daar"})

while True:
    node_p2p1.send_to_nodes({"node": "Node 1", "test": "ha", "ni": "hao"})
    time.sleep(1)

print("main stopped")

