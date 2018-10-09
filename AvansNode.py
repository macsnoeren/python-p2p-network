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
# AvansNode ###########################################################################################################
#######################################################################################################################

class AvansNode (TcpServerNode.Node):

    # AvansNode Constructor
    #
    def __init__(self, host, port):
        super(AvansNode, self).__init__(host, port, None)

        self.rsa_key = RSA.generate(2048)

        self.discovery_messages = {}

        print("MyPeer2PeerNode: Started")

    # This function makes sure that a complex dict variable (consisting of
    # other dicts and lists, is converted to a unique string that can be
    # hashed. Every data object that contains the same values, should result
    # into the dame unique string.
    #
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

    # Returns the hased version of the data dict. The dict can contain lists and dicts, but
    # it must be based as dict.
    #
    def get_hash(self, data):
        #message = str(data).replace(" ", "")
        message = self.get_data_uniq_string(data)
        h = SHA256.new() # SHA2 / 256
        h.update(message.encode("utf-8"))
        return h.hexdigest()

    # Return the public key that is generated or loaded for this node.
    #
    def get_public_key(self):
        return self.rsa_key.publickey().exportKey("PEM");

    # Get the private key that is generated or loaded for this node.
    #
    def get_private_key(self):
        return self.rsa_key.exportKey("PEM");

    # Encrypt a message using a public key, most of the time from someone else
    #
    def encrypt(self, message, public_key):
        key = RSA.importKey(public_key)
        cipher = PKCS1_v1_5_Cipher.new(key)
        return b64encode( cipher.encrypt(message) )

    # Decrypt a ciphertext message that has been encrypted with our public key by
    # someone else.
    #
    def decrypt(self, ciphertext):
        ciphertext = b64decode( ciphertext )
        cipher = PKCS1_v1_5_Cipher.new(self.rsa_key)
        sentinal = "sentinal"
        return cipher.decrypt(ciphertext, sentinal)

    # Sign the message using our private key
    #
    def sign(self, message):
        h = SHA.new(message)
        signer = PKCS1_v1_5_Signature.new(self.rsa_key)
        return b64encode( signer.sign(h) )

    # Sign the data, with is hashed, with our private key.
    #
    def sign_data(self, data):
        message = self.get_data_uniq_string(data)
        return self.sign(message);

    # Verify the signature, based on the message, public key and signature.
    #
    def verify(self, message, public_key, signature):
        signature = b64decode( signature )
        key = RSA.importKey(public_key)
        h = SHA.new(message)
        verifier = PKCS1_v1_5_Signature.new(key)
        return verifier.verify(h, signature)

    # Verify the signature, based on the data, public key and signature.
    #
    def verify_data(self, data, public_key, signature):
        message = self.get_data_uniq_string(data)
        return self.verify(message, public_key, signature);

    # This method can be overrided when a different nodeconnection is required!
    def create_new_connection(self, connection, client_address, callback):
        return AvansNodeConnection(self, connection, client_address, callback)

    def send_data(self, type, data):
        data['_type'] = type
        self.send_to_nodes(data)

    ##########################################################
    # Method override, implement here your own functionality #
    ##########################################################    

    # When a node is connected to us, this event is launched!
    #
    def event_node_connected(self, node):
        super(AvansNode, self).event_node_connected(node)
        self.send_details(node)

    # When we connect to a node and it is successfull, this event is launched.
    #
    def event_connected_with_node(self, node):
        super(AvansNode, self).event_connected_with_node(node)

    # When a node, that had made a connection to us, is closing the connection,
    # this event is launched
    #
    def event_node_inbound_closed(self, node):
        super(AvansNode, self).event_node_inbound_closed(node)

    # When a node, that we have made contact with, is closing the connection,
    # this event is launched.
    #
    def event_node_outbound_closed(self, node):
        super(AvansNode, self).event_node_outbound_closed(node)
        print("p2p_event_node_outbound_closed: " + node.getName())

    # If a message comes in fro mthe nodes, determine what to do!
    #
    def event_node_message(self, node, data):
        super(AvansNode, self).event_node_message(node)
        
        if (data['_type'] == 'ping'):
            self.received_ping(node, data)

        elif (data['_type'] == 'pong'):
            self.received_pong(node, data)

        elif (data['_type'] == 'node-details'):
            self.received_details(node, data)

        elif (data['_type'] == 'discovery'):
            self.received_discovery(node, data)

        elif (data['_type'] == 'discovery_answer'):
            self.received_discovery_answer(node, data)

        else:
            print("p2p_event_node_message: message type unknown: " + node.getName() + ": " + str(data))

    #######################################################
    # GETTING/SENDING NODE DETAILS                        #
    #######################################################

    def send_details(self, node):
        node.send({'_type': 'node-details', 'public_key': self.get_public_key(), 'id': self.get_id() })
        node.set_public_key_send()

    def received_details(self, node, data):
        node.set_public_key(data['public_key'])
        if ( node.get_public_key_send() == False ):
            self.send_details(node)
            node.set_public_key_send()

    #######################################################
    # PING / PONG Message packet                          #
    #######################################################

    # A ping request is send to all the nodes that are connected
    def send_ping(self):
        self.send_data('ping', {'timestamp': time.time(), 'id': self.get_id()})

    # A pong request is only send to the node that has send the ping request
    def send_pong(self, node, timestamp):
        #self.send_to_node(node, {'_type': 'pong', 'timestamp': timestamp, 'timestamp_node': time.time()})
        node.send({'_type': 'pong', 'timestamp': timestamp, 'timestamp_node': time.time(), 'id': self.get_id()})

    # With a ping message, return a pong message to the node
    def received_ping(self, node, data):
        self.send_pong(node, data['timestamp'])

    # Got message back based on our ping message, check the latency of the node!
    def received_pong(self, node, data):
        latency = time.time() - data['timestamp']

    #######################################################
    # DISCOVERY                                           #
    #######################################################

    def send_discovery(self):
        self.send_data('discovery', { 'id': self.get_id(), 'timestamp': time.time() })

    def send_discovery_answer(self, node, data):
        nodes = []
        for n in self.get_inbound_nodes():
            nodes.append({'id': n.get_id(), 'ip': n.get_host(), 'port': n.nodeServer.get_port(), 'connection': 'inbound'})
        for n in self.get_outbound_nodes():
            nodes.append({'id': n.get_id(), 'ip': n.get_host(), 'port': n.get_port(), 'connection': 'outbound'})

        node.send({'id': data['id'], '_type': 'discovery_answer', 'timestamp': data['timestamp'], 'nodes': nodes})

    # Got a discovery request, send back a discover_anwser_message with my details
    # and relay it to the other hosts, when I got the answers from them  send it thourgh
    # This means i need to administer these message
    #
    def received_discovery(self, node, data):
        if data['id'] in self.discovery_messages:
            print("discovery_message: message already received, so not sending it")

        else:
            print("discovery_message: process message")
            self.discovery_messages[data['id']] = node
            self.send_discovery_answer(node, data)
            self.send_to_nodes({'_type': 'discovery', 'id': data['id'], 'timestamp': data['timestamp']}, [node])

    def received_discovery_answer(self, node, data):
        if data['id'] in self.discovery_messages: # needs to be relayed
            self.send_discovery_answer(self.discovery_messages[data['id']], data)

        else:
            if ( data['id'] == self.get_id() ):
                print("discovery_message_answer: This is for me!: " + str(data) + ":" + str(time.time()-data['timestamp']))

            else:
                print("unknwon state!")

    # Transations

    def send_transacation(self, sender, receiver, amount):
        self.send_data('transaction',
                        {'sender': sender,
                         'receiver': receiver,
                         'amount': amount
                        })

    def transaction_message(self, node, data):
        print("Transaction message")

    ### Implementation messages received!


####################################################################################################
# AvansNodeConnection                                                                              #
####################################################################################################

class AvansNodeConnection(TcpServerNode.NodeConnection):

    # Python constructor
    def __init__(self, nodeServer, sock, clientAddress, callback):
        super(AvansNodeConnection, self).__init__(nodeServer, sock, clientAddress, callback)

        # The public key that we have received from the node that we are connected to
        self.remote_node_public_key = ""
        self.remote_node_has_public_key = False # Whether we have send the public key

    def get_public_key_send(self):
        return self.remote_node_has_public_key

    def set_public_key_send(self):
        self.remote_node_has_public_key = True
        
    def set_public_key(self, key):
        self.remote_node_public_key = key

    def get_public_key(self):
        return self.remote_node_public_key

    def check_message(self, data):
        signature  = data['_signature']
        public_key = data['_public_key']
        hash       = data['_hash']
        message_id = data['_message_id']
        timestamp  = data['_timestamp']

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
        data['_signature']  = signature
        data['_public_key'] = public_key
        data['_hash']       = hash
        data['_message_id'] = message_id
        data['_timestamp']  = timestamp
                
        return True

    def create_message(self, data):
        super(AvansNodeConnection, self).create_message(data)

        data['_id']         = self.nodeServer.get_id()
        data['_timestamp']  = time.time()
        data['_message_id'] = self.nodeServer.get_hash(data)
        data['_hash']       = self.nodeServer.get_hash(data)
        data['_signature']  = self.nodeServer.sign_data(data)
        data['_public_key'] = self.nodeServer.get_public_key()

        return data;
