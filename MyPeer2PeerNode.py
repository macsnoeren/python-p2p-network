#######################################################################################################################
# AVANS - BLOCKCHAIN - MINOR MAD                                                                                      #
#                                                                                                                     #
# Author: Maurice Snoeren                                                                                             #
# Version: 0.1 beta (use at your own risk)                                                                            #
#                                                                                                                     #
# MyPeer2PeerNode is an example how to use the TcpServerNode to implement your own peer-to-peer network node based on #
# the TcpServerNode Node class.                                                                                       #
#######################################################################################################################

import TcpServerNode

#######################################################################################################################
# MyPeer2PeerNode #####################################################################################################
#######################################################################################################################

class MyPeer2PeerNode (TcpServerNode.Node):

    # Python class constructor
    def __init__(self, host, port):
        super(MyPeer2PeerNode, self).__init__(host, port, None)

        print("MyPeer2PeerNode: Started")

    # Method override, implement here your own functionality
    def event_node_connected(self, node):
        print("p2p_event_node_connected: " + node.getName())

    def event_connected_with_node(self, node):
        print("p2p_event_node_connected: " + node.getName())

    def event_node_inbound_closed(self, node):
        print("p2p_event_node_inbound_closed: " + node.getName())

    def event_node_outbound_closed(self, node):
        print("p2p_event_node_outbound_closed: " + node.getName())

    # If a message comes in, determines what to do!
    def event_node_message(self, node, data):
        print("p2p_event_node_message: " + node.getName() + ": " + str(data))
