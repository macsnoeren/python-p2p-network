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
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_v1_5_Cipher
from Crypto.Signature import PKCS1_v1_5 as PKCS1_v1_5_Signature
from Crypto.Hash import SHA256, SHA
from base64 import b64decode, b64encode

#######################################################################################################################
# MyPeer2PeerNode #####################################################################################################
#######################################################################################################################

class AvansNode (TcpServerNode.Node):

    # Python class constructor
    def __init__(self, host, port):
        super(AvansNode, self).__init__(host, port, None)

        self.rsa_key = RSA.generate(2048)

        self.discovery_messages = {}

        print("MyPeer2PeerNode: Started")

    # This function makes sure that a complex dict variable (consisting of
    # other dicts and lists, is converted to a unique string that can be
    # hashed. Every data object that contains the same values, should result
    # into the dame unique string.
    def get_data_uniq_string(self, data):
        uniq = ""        
        if ( isinstance(data, dict) ):
            for key in sorted(data):
                uniq = uniq + key + self.get_data_uniq_string(data[key]).replace("\n", "-n")

        else:
            if ( isinstance(data, list) ):
                for element in sorted(data):
                    uniq = uniq + self.get_data_uniq_string(element).replace("\n", "-n")

            else:
                uniq =  uniq + str(data).replace("\n", "-n")

        return uniq
    
    def get_hash(self, data):
        #message = str(data).replace(" ", "")
        message = self.get_data_uniq_string(data)
        h = SHA256.new() # SHA2 / 256
        h.update(message.encode("utf-8"))
        return h.hexdigest()

    def get_public_key(self):
        return self.rsa_key.publickey().exportKey("PEM");

    def get_private_key(self):
        return self.rsa_key.exportKey("PEM");

    def encrypt(self, message, public_key):
        key = RSA.importKey(public_key)
        cipher = PKCS1_v1_5_Cipher.new(key)
        return b64encode( cipher.encrypt(message) )

    def decrypt(self, ciphertext):
        ciphertext = b64decode( ciphertext )
        cipher = PKCS1_v1_5_Cipher.new(self.rsa_key)
        sentinal = "sentinal"
        return cipher.decrypt(ciphertext, sentinal)

    def sign(self, message):
        h = SHA.new(message)
        signer = PKCS1_v1_5_Signature.new(self.rsa_key)
        return b64encode( signer.sign(h) )

    def sign_data(self, data):
        message = self.get_data_uniq_string(data)
        return self.sign(message);

    def verify(self, message, public_key, signature):
        signature = b64decode( signature )
        key = RSA.importKey(public_key)
        h = SHA.new(message)
        verifier = PKCS1_v1_5_Signature.new(key)
        return verifier.verify(h, signature)
    
    def verify_data(self, data, public_key, signature):
        message = self.get_data_uniq_string(data)
        return self.verify(message, public_key, signature);

    # This method can be overrided when a different nodeconnection is required!
    def create_new_connection(self, connection, client_address, callback):
        return AvansNodeConnection(self, connection, client_address, callback)

    # Method override, implement here your own functionality
    def event_node_connected(self, node):
        print("p2p_event_node_connected: " + node.getName())
        self.send_details(node)

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

        elif (data['_type'] == 'node-details'):
            self.receive_details(node, data)

        elif (data['_type'] == 'discovery'):
            self.discovery_message(node, data)

        elif (data['_type'] == 'discovery_answer'):
            self.discovery_message_answer(node, data)

        else:
            print("p2p_event_node_message: message type unknown: " + node.getName() + ": " + str(data))

    #######################################################
    # GETTING/SENDING NODE DETAILS                        #
    #######################################################

    def send_details(self, node):
        node.send({'_type': 'node-details', 'public_key': self.get_public_key(), 'id': self.get_id() })

    def receive_details(self, node, data):
        print("got node details: " + str(data))
        node.set_public_key(data['public_key'])
        if ( node.get_public_key() == "" ):
            self.send_details(node)


    #######################################################
    # PING / PONG Message packet                          #
    #######################################################

    # A ping request is send to all the nodes that are connected
    def send_ping(self):
        self.send_data('ping', {'timestamp': time.time()})

    # A pong request is only send to the node that has send the ping request
    def send_pong(self, node, timestamp):
        #self.send_to_node(node, {'_type': 'pong', 'timestamp': timestamp, 'timestamp_node': time.time()})
        node.send({'_type': 'pong', 'timestamp': timestamp, 'timestamp_node': time.time()})

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

        node.send({'id': data['id'], '_type': 'discovery_answer', 'timestamp': data['timestamp'], 'nodes': nodes})

    # Got a discovery request, send back a discover_anwser_message with my details
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

    def send_transacation(self, sender, receiver, amount):
        self.send_data('transaction',
                        {'sender': sender,
                         'receiver': receiver,
                         'amount': amount
                        })

    def send_data(self, type, data):
        data['_type'] = type
        self.send_to_nodes(data)

    ### Implementation messages received!

    def transaction_message(self, node, data):
        print("Transaction message")

####################################################################################################
# AvansNodeConnection                                                                              #
####################################################################################################

class AvansNodeConnection(TcpServerNode.NodeConnection):

    # Python constructor
    def __init__(self, nodeServer, sock, clientAddress, callback):
        super(AvansNodeConnection, self).__init__(nodeServer, sock, clientAddress, callback)

        # The public key that we have received from the node that we are connected to
        self.remote_node_public_key = ""

    def set_public_key(self, key):
        self.remote_node_public_key = key

    def get_public_key(self):
        return self.remote_node_public_key

    def check_message(self, data):
        signature  = data['_signature']
        public_key = data['_public_key']#self.get_public_key()
        hash       = data['_hash']
        message_id = data['_message_id']
        timestamp  = data['_timestamp']

        # Hier BEN IK
        #if ( 'public_key' in data ):
        #    public_key = data['_public_key']

        #print("PUBLIC: KEY: " + self.get_public_key()) # Use the public key of the node to check?
        #data['add'] = "asdasd" # Change the message for testing!

        # 1. Check the signature!
        del data['_public_key']
        del data['_signature']
        if ( self.nodeServer.verify_data(data, public_key, signature) == False):
            print("Signature not correct!")
            return False
        
        # 2. Check the hash
        del data['_hash']
        if ( self.nodeServer.get_hash(data) != hash ):
            print("Hash not correct!")
            return False

        # 3. Check the message id
        del data['_message_id']
        if ( self.nodeServer.get_hash(data) != message_id ):
            print("Message ID not correct!")
            return False

        # 4. Restore the data
        data['_hash']       = hash
        data['_message_id'] = message_id
        data['_timestamp']  = timestamp
                
        return True

    def create_message(self, data):
        super(AvansNodeConnection, self).create_message(data)

        data['_timestamp'] = time.time()
        data['_message_id'] = self.nodeServer.get_hash(data)
        data['_hash'] = self.nodeServer.get_hash(data)
        data['_signature'] = self.nodeServer.sign_data(data)
        data['_public_key'] = self.nodeServer.get_public_key()

        return data;

# EXAMPLE:
#        ciphertext = self.encrypt("Maurice Snoeren", self.get_public_key())
#        print("CT: " + ciphertext)
#
#        message = self.decrypt(ciphertext)
#        print("MS: " + message)
#
#        signature = self.sign("Maurice Snoeren")
#        print("SG: " + str(signature))
#
#        if ( self.verify(message, self.get_public_key(), signature) ):
#            print "YES!!"
#        else:
#            print "NOOO!"

