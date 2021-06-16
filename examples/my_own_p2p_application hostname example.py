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

from MyOwnPeer2PeerNode_local_hostname_example import MyOwnPeer2PeerNode

import socket

# test the connection to google's dns server:
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))

# get the local IP address from the networked adapter:
ip = s.getsockname()[0]

# get the local computer hostname:
id = socket.gethostname()
s.close()

# id is added as a third argument and ip can be used to replace the first argument:
node_1 = MyOwnPeer2PeerNode("127.0.0.1", 8001, id)
node_2 = MyOwnPeer2PeerNode("127.0.0.1", 8002, id)
node_3 = MyOwnPeer2PeerNode("127.0.0.1", 8003, id)

time.sleep(1)

node_1.start()
node_2.start()
node_3.start()

time.sleep(1)

node_1.connect_with_node('127.0.0.1', 8002)
node_2.connect_with_node('127.0.0.1', 8003)
node_3.connect_with_node('127.0.0.1', 8002)

time.sleep(2)

node_1.send_to_nodes("message: Hi there!")

time.sleep(5)

node_1.stop()
node_2.stop()
node_3.stop()
print('end test')
