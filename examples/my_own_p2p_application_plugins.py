#######################################################################################################################
# Author: Maurice Snoeren                                                                                             #
# Version: 0.1 beta (use at your own risk)                                                                            #
#                                                                                                                     #
# This example show how to derive a own Node class (MyOwnPeer2PeerNode) from p2pnet.Node to implement your own Node   #
# implementation. See the MyOwnPeer2PeerNode.py for all the details. In that class all your own application specific  #
# details are coded.                                                                                                  #
#######################################################################################################################

import sys
import time
sys.path.insert(0, '..') # Import the files where the modules are located

from p2pnetwork.node import Node
from p2pnetwork.plugins.network_discovery import PluginNetworkDiscovery

node_1 = Node("127.0.0.1", 8001, 1)
networkdiscovery_1 = PluginNetworkDiscovery()
node_1.register_plugin(networkdiscovery_1)

node_2 = Node("127.0.0.1", 8002, 2)
networkdiscovery_2 = PluginNetworkDiscovery()
node_2.register_plugin(networkdiscovery_2)

#node_3 = Node("127.0.0.1", 8003, 3)
#networkdiscovery_3 = PluginNetworkDiscovery()


time.sleep(1)

node_1.start()
#node_2.start()
#node_3.start()

time.sleep(1)

debug = True
node_1.debug = debug
#node_2.debug = debug
#node_3.debug = debug


#node_1.connect_with_node('127.0.0.1', 8002)
#node_2.connect_with_node('127.0.0.1', 8003)
#node_3.connect_with_node('127.0.0.1', 8001)

#time.sleep(2)

#node_1.send_to_nodes("message: Hi there!")

#time.sleep(2)

print("node 1 is stopping..")
node_1.stop()

#time.sleep(20)

#node_2.send_to_nodes("message: Hi there node 2!")
#node_2.send_to_nodes("message: Hi there node 2!")
#node_2.send_to_nodes("message: Hi there node 2!")
#node_3.send_to_nodes("message: Hi there node 2!")
#node_3.send_to_nodes("message: Hi there node 2!")
#node_3.send_to_nodes("message: Hi there node 2!")

#time.sleep(10)

#time.sleep(5)

node_1.stop()
#node_2.stop()
#node_3.stop()

print('end test')
