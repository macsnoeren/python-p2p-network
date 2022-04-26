import time

from p2pnetwork.plugin import NodePlugin

"""
Author: Maurice Snoeren <macsnoeren(at)gmail.com>
Version: 0.1 beta (use at your own risk)
Date: 22-4-2022

Python package p2pnet for implementing decentralized peer-to-peer network applications
"""

class PluginNetworkDiscovery(NodePlugin):
    """This plugin implements the network functionality of the p2p network."""
       
    def __init__(self):
        """Create instance of PluginNetworkDiscovery."""
        super().__init__()

        # Store the ids of the discover messages that have been received
        # together with the node that send this message
        self.discover_ids = {}

    def node_message(self, node, data) -> bool:
        if data["type"] == "discover":
            self.discover_received(node, data)
            return True

        # Handle the reception of the discover_answer message
        if data["type"] == "discover_answer":
            self.discover_answer_received(node, data)
            return True

        return False

    # Start discovery of nodes in the network. The depth determines how
    # many times the message should be relayed. Default depth is -1, 
    # which means that it will be infinitely be relayed. Note that nodes
    # will not relay the discovery message when they already received it.
    def discover(self, depth=-1):
        id = self.id + str(int(time.time())) # node_id + timestamp
        self.getNode().send_to_nodes({
            "type": "discover",
            "id": id,
            "depth": depth
        })
        self.discover_ids[id] = None

    def discover_received(self, node, data):
        # 1. Drop the discover message has been received previously. Register these id's in an array for example.
        if data["id"] in self.discover_ids.keys():
            print("discover_received: drop message already received")
            return
        
        # 2. Drop the discover message when depth is zero.
        if data["depth"] == 0:
            print("discover_received: drop message depth is zero")
            return

        # 3. If depth is not -1 decrement depth with 1
        if data["depth"] != -1:
            data["depth"] = data["depth"] - 1

        # 4. Register the id in an array
        self.discover_ids[data["id"]] = node

        # 5. Send discover_answer to sender (see discover_answer message)
        self.discover_answer(node, data["id"])

        # 6. If depth is -1 and not 0 send the message to connected nodes
        if data["depth"] == -1 and data["depth"] != 0:
            self.getNode().send_to_nodes(data)

    def discover_answer(self, node, id):
        outbound_nodes = []
        inbound_nodes = []

        for node in self.nodes_outbound:
            outbound_nodes.append({
                "id": node.id,
                "host": node.host,
                "port": node.port
            })

        for node in self.nodes_inbound:
            inbound_nodes.append({
                "id": node.id,
                "host": node.host,
                "port": node.port
            })

        self.getNode().send_to_nodes({
            "type": "discover_answer",
            "id": id,
            "node_id": self.id,
            "outbound_nodes": outbound_nodes,
            "inbound_nodes": inbound_nodes
        })        

    def discover_answer_received(self, node, data):
        # 1. Drop the message when the id is not registered, in this case it is a fake message? You could flag this node as possible malicious? But that will not be handled here.
        if data["id"] not in self.discover_ids.keys():
            print("discover_answer_received: drop message fake?")
            return
        
        # 2. When the registration of the id shows that it was send by another node, then relay the message to that node
        if self.discover_ids[data["id"]] != None:
            self.getNode().send_to_node(self.discover_ids[data["id"]], data)

        else: # 3. When the registration of the id shows that it is the current node, then process the data within the node by calling another method
            self.discover_answer_process(data)

    def discover_answer_process(self, data):
        print("discover_answer_process: process the data: ")
        print(data)

    def __str__(self):
        return str(self.__class__.__name__)

    def __repr__(self):
        return str(self.__class__)
