#######################################################################################################################
# AVANS - BLOCKCHAIN - MINOR MAD                                                                                      #
#                                                                                                                     #
# Author: Maurice Snoeren                                                                                             #
# Version: 0.1 beta (use at your own risk)                                                                            #
#                                                                                                                     #
# MyPeer2PeerNode is an example how to use the TcpServerNode to implement your own peer-to-peer network node based on #
# the TcpServerNode Node class.                                                                                       #
#######################################################################################################################

import time
import TcpServerNode
import hashlib
import rsa
from base64 import b64decode, b64encode

#######################################################################################################################
# MyPeer2PeerNode #####################################################################################################
#######################################################################################################################

class AvansNode (TcpServerNode.Node):

    # Python class constructor
    def __init__(self, host, port):
        super(AvansNode, self).__init__(host, port, None)

        (self.pubkey, self.privkey) = rsa.newkeys(1024)

        print( b64encode(self.pubkey))

        self.discovery_messages = {}

        print("MyPeer2PeerNode: Started")

    def get_hash(self, data):
        message = str(data).replace(" ", "")
        h = hashlib.new("sha3_256")
        h.update(message.encode("utf-8"))
        return h.hexdigest()

    def get_public_key(self):
        return self.pubkey

    def sign(self, data):
        message = str(data).replace(" ", "")
        signature = rsa.sign(message.encode("utf-8"), self.privkey, 'SHA-1').hex()
        return signature

    def verify(self, signature, message):
        try:
            return rsa.verify( message.encode("utf-8"), bytes.fromhex(signature), self.get_public_key() )
        except:
            return False

    # This method can be overrided when a different nodeconnection is required!
    def create_new_connection(self, connection, client_address, callback):
        return AvansNodeConnection(self, connection, client_address, callback)

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
        if (data['_type'] == 'ping'):
            self.ping_message(node, data)

        elif (data['_type'] == 'pong'):
            self.pong_message(node, data)

        elif (data['_type'] == 'discovery'):
            self.discovery_message(node, data)

        elif (data['_type'] == 'discovery_answer'):
            self.discovery_message_answer(node, data)

        else:
            print("p2p_event_node_message: message type unknown: " + node.getName() + ": " + str(data))

    #######################################################
    # PING / PONG Message packet                          #
    #######################################################

    # A ping request is send to all the nodes that are connected
    def send_ping(self):
        self.send_data('ping', {'timestamp': time.time()})

    # A pong request is only send to the node that has send the ping request
    def send_pong(self, node, timestamp):
        self.send_to_node(node, {'_type': 'pong', 'timestamp': timestamp, 'timestamp_node': time.time()})

    # With a ping message, return a pong message to the node
    def ping_message(self, node, data):
        self.send_pong(node, data['timestamp'])

    # Got message back based on our ping message, check the latency of the node!
    def pong_message(self, node, data):
        latency = time.time() - data['timestamp']

    #######################################################
    # DISCOVERY                                           #
    #######################################################

    def send_discovery_message(self):
        self.send_data('discovery', { 'id': self.get_id(), 'timestamp': time.time() })

    def send_discovery_answer_message(self, node, data):
        nodes = []
        for n in self.get_inbound_nodes():
            nodes.append({'id': n.get_id(), 'ip': n.get_host(), 'port': n.nodeServer.get_port(), 'connection': 'inbound'})
        for n in self.get_outbound_nodes():
            nodes.append({'id': n.get_id(), 'ip': n.get_host(), 'port': n.get_port(), 'connection': 'outbound'})

        self.send_to_node(node, {'id': data['id'], '_type': 'discovery_answer', 'timestamp': data['timestamp'], 'nodes': nodes})

    # Got a discovery request, send back a discover_anser_message with my details
    # and relay it to the other hosts, when I got the answers from them  send it thourgh
    # This means i need to administer these message
    def discovery_message(self, node, data):
        if data['id'] in self.discovery_messages:
            print("discovery_message: message already received, so not sending it")

        else:
            print("discovery_message: process message")
            self.discovery_messages[data['id']] = node
            self.send_discovery_answer_message(node, data)
            self.send_to_nodes({'_type': 'discovery', 'id': data['id'], 'timestamp': data['timestamp']}, [node])

    def discovery_message_answer(self, node, data):
        if data['id'] in self.discovery_messages: # needs to be relayed
            self.send_discovery_answer_message(self.discovery_messages[data['id']], data)

        else:
            if ( data['id'] == self.get_id() ):
                print("discovery_message_answer: This is for me!: " + str(data) + ":" + str(time.time()-data['timestamp']))

            else:
                print("unknwon state!")

        print("Discovery message: " + str(data))

    def send_transacation(self, sender, receiver, amount):
        self.send_data('transaction',
                        {'sender': sender,
                         'receiver': receiver,
                         'amount': amount
                        })

    # Maybe add a hash at sending? When receiving check the hash and use it for check if your already had it.
    def send_data(self, type, data):
        data['_type'] = type
        self.send_to_nodes(data)

    ### Implementation messages received!

    def transaction_message(self, node, data):
        print("Transaction message")

class AvansNodeConnection(TcpServerNode.NodeConnection):

    # Python constructor
    def __init__(self, nodeServer, sock, clientAddress, callback):
        super(AvansNodeConnection, self).__init__(nodeServer, sock, clientAddress, callback)

        self.remote_node_public_key = "put here the public key of the remote node, for validation"
        self.remote_node_key = "secure key"

    def create_message(self, data):
        super(AvansNodeConnection, self).create_message(data)

        data['_timestamp'] = time.time()
        data['_message_id'] = self.nodeServer.get_hash(data)
        data['_hash'] = self.nodeServer.get_hash(data)
        data['_public_key'] = self.nodeServer.get_public_key()
        data['_signature'] = self.nodeServer.sign(data)

        print("MESSAGE CREATED: " + str(data))

        return data;
