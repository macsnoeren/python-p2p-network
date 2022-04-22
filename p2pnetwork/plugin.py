from abc import abstractmethod
from p2pnetwork.node import Node

"""
Author: Maurice Snoeren <macsnoeren(at)gmail.com>
Version: 0.1 beta (use at your own risk)
Date: 22-4-2022

Python package p2pnet for implementing decentralized peer-to-peer network applications
"""

class NodePlugin:
    """Implements the base class that can be used to implement plugins for the node. These plugins can
       be added to the Node. The node calls the plugin methods when events occur. Using plugins new 
       functionality can be added to the Node. All plugins are required to extend from this base class.
       This base class provides the interface that is required to be implemented."""
       
    def __init__(self):
        """Create instance of NodePlugin."""

        # The node that the plugin holds, required to call function to the node.
        self.node[Node] = None

        # Fill in the name of the plugin
        self.name = ""

        # Fill in the desciption of the plugin
        self.descripion = ""

    def set_node_reference(self, node:Node) -> None:
        """Methods sets the reference to the Node. This can be done once and it will check if
           it has a reference to Node itself."""
        if self.node == Node:
            self.node = node
        else:
            print("NodePlugin: Can only reference to a Node once!")

    def outbound_node_connected(self, node) -> bool:
        """The plugin is able to react on outbound nodes that are connected using this method."""
        return False
        
    def inbound_node_connected(self, node) -> bool:
        """The plugin is able to react on inbound nodes that are connected using this method."""
        return False

    def inbound_node_disconnected(self, node) -> bool:
        """The plugin is able to react on inbound nodes that are disconnected using this method."""
        return False

    def outbound_node_disconnected(self, node) -> bool:
        """The plugin is able to react on outbound nodes that are disconnected using this method."""
        return False

    def node_disconnect_with_outbound_node(self, node) -> bool:
        """The plugin is able to react on disconnection with outbound node."""
        return False

    def node_message(self, node, data) -> bool:
        """This method is called when the node received data from another node. The plugin is able to check
           whether this method is required to be processed. When the plugin decides that the data is going
           to be processed, it returns True otherwise False."""
        return False

    def __str__(self):
        return 'NodePlugin'

    def __repr__(self):
        return '<NodePlugin>'
