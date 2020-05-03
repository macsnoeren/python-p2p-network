#######################################################################################################################
# Author: Maurice Snoeren                                                                                             #
# Version: 0.1 beta (use at your own risk)                                                                            #
#                                                                                                                     #
# SecureNode                                                                                                          #
#######################################################################################################################
import time
import json
import hashlib

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_v1_5_Cipher
from Crypto.Signature import PKCS1_v1_5 as PKCS1_v1_5_Signature
from Crypto.Hash import SHA512
from base64 import b64decode, b64encode

from p2pnet.node import Node

class SecureNode (Node):
    __doc__= '''
    Class SecurityNode:
    This class is a concrete implementation of the node class and communicates with JSON between the nodes. 
    It implements a secure communication between the nodes. Not that the communication is encrypted, but
    more on the tampering aspect. Messages are checked on the integrity (due to signing). A public/private
    RSA key infrastructure is used to implement this. Furthermore, it implements a basic ping/pong system and
    discovery. Using this node, you are able to implement your own protocol on top. All messages that are send
    (make sure you use create_message method) are signed and checked when received.
    '''

    # Python class constructor
    def __init__(self, host, port):
        super(SecureNode, self).__init__(host, port, None)

        # Track the discovery message that are recieved, so we know when to stop!
        self.discovery_messages = {}

        # The RSA public/private key from this node
        # TODO: Get it from a file from the outside, well protected!!
        # TODO: Maybe with password protection from the user that starts the node?!
        self.rsa_key = RSA.generate(2048)

    ## EVENTS

    def outbound_node_connected(self, connected_node):
        print("outbound_node_connected: " + connected_node.id)
        
    def inbound_node_connected(self, connected_node):
        print("inbound_node_connected: " + connected_node.id)

    def inbound_node_disconnected(self, connected_node):
        print("inbound_node_disconnected: " + connected_node.id)

    def outbound_node_disconnected(self, connected_node):
        print("outbound_node_disconnected: " + connected_node.id)

    # Implement here the messages that are inserted.
    def node_message(self, connected_node, message):
        try:
            data = json.loads(message)
            print("node_message from " + connected_node.id + ": " + str(data))

            if not self.check_message(data):
                print("Received message is corrupted!")

            if ( '_type' in data ):
                if (data['_type'] == 'ping'):
                    self.received_ping(connected_node, data)

                elif (data['_type'] == 'pong'):
                    self.received_pong(connected_node, data)
                    
                elif (data['_type'] == 'discovery'):
                    self.received_discovery(connected_node, data)

                elif (data['_type'] == 'discovery_answer'):
                    self.received_discovery_answer(connected_node, data)

                else:
                    self.debug_print("p2p_event_node_message: message type unknown: " + connected_node.id + ": " + str(data))

        except Exception as e:
            self.debug_print("NodeConnection: Data could not be parsed (%s) (%s)" % (message, str(e)))
       
    def node_disconnect_with_outbound_node(self, connected_node):
        print("node wants to disconnect with oher outbound node: " + connected_node.id)
        
    def node_request_to_stop(self):
        print("node is requested to stop!")
        self.send_to_nodes("")

    ## Extra application specific implementation!

    def create_message(self, data):
        # Somehow the data is not always cleaned up!
        for el in ['_id', '_timestamp', '_message_id', '_hash', '_signature', '_public_key']:
            if ( el in data ):
                del data[el]

        try:
            data['_mcs']        = self.message_count_send
            data['_mcr']        = self.message_count_recv
            data['_id']         = self.id
            data['_timestamp']  = time.time()
            data['_message_id'] = self.get_hash(data)

            self.debug_print("Message creation:")
            self.debug_print("Message hash based on: " + self.get_data_uniq_string(data))

            data['_hash']       = self.get_hash(data)

            self.debug_print("Message signature based on: " + self.get_data_uniq_string(data))

            data['_signature']  = self.sign_data(data)
            data['_public_key'] = self.get_public_key().decode('utf-8')

            self.debug_print("_hash: " + data['_hash'])
            self.debug_print("_signature: " + data['_signature'])

            return json.dumps(data, separators=(',', ':'))

        except Exception as e:
            self.debug_print("Failed to create message " + str(e))

    # Check the message hashed and if the signature matches the public key
    # TODO: if a node is known, the public key should be stored, so this could not be changed by the
    #       node in the future.
    def check_message(self, data):
        self.debug_print("incoming message information:")
        self.debug_print("_hash: " + data['_hash'])
        self.debug_print("_signature: " + data['_signature'])

        signature  = data['_signature']
        public_key = data['_public_key']
        data_hash  = data['_hash']
        message_id = data['_message_id']
        timestamp  = data['_timestamp']

        #print("PUBLIC: KEY: " + self.get_public_key()) # Use the public key of the node to check?
        #data['add'] = "asdasd" # Change the message for testing!

        # 1. Check the signature!
        del data['_public_key']
        del data['_signature']
        checkSignature = self.verify_data(data, public_key, signature)
        
        # 2. Check the hash of the data
        del data['_hash']
        checkDataHash = (self.get_hash(data) == data_hash)

        # 3. Check the message id
        del data['_message_id']
        checkMessageId = (self.get_hash(data) == message_id)

        # 4. Restore the data
        data['_signature']  = signature
        data['_public_key'] = public_key
        data['_hash']       = data_hash
        data['_message_id'] = message_id
        data['_timestamp']  = timestamp

        self.debug_print("Checking incoming message:")
        self.debug_print(" signature : " + str(checkSignature))
        self.debug_print(" data hash : " + str(checkDataHash))
        self.debug_print(" message id: " + str(checkMessageId))

        return checkSignature and checkDataHash and checkMessageId

    def send_message(self, message):
        self.send_to_nodes(self.create_message({ "message": message }))

    # This function makes sure that a complex dict variable (consisting of
    # other dicts and lists, is converted to a unique string that can be
    # hashed. Every data object that contains the same values, should result
    # into the dame unique string.
    def get_data_uniq_string(self, data):
        return json.dumps(data, sort_keys=True)
        
    # Returns the hased version of the data dict. The dict can contain lists and dicts, but
    # it must be based as dict.
    def get_hash(self, data):
        try:
            h = hashlib.sha512()
            message = self.get_data_uniq_string(data)

            self.debug_print("Hashing the data:")
            self.debug_print("Message: " + message)

            h.update(message.encode("utf-8"))

            self.debug_print("Hash of the message: " + h.hexdigest())

            return h.hexdigest()

        except Exception as e:
            print("Failed to hash the message: " + str(e))

    # Return the public key that is generated or loaded for this node.
    def get_public_key(self):
        return self.rsa_key.publickey().exportKey("PEM")

    # Get the private key that is generated or loaded for this node.
    def get_private_key(self):
        return self.rsa_key.exportKey("PEM")

    # Encrypt a message using a public key, most of the time from someone else
    def encrypt(self, message, public_key):
        try:
            key = RSA.importKey(public_key)
            cipher = PKCS1_v1_5_Cipher.new(key)
            return b64encode( cipher.encrypt(message) )

        except Exception as e:
            print("Failed to encrypt the message: " + str(e))

    # Decrypt a ciphertext message that has been encrypted with our public key by
    # someone else.
    def decrypt(self, ciphertext):
        try:
            ciphertext = b64decode( ciphertext )
            cipher = PKCS1_v1_5_Cipher.new(self.rsa_key)
            sentinal = "sentinal" # What is this again?
            return cipher.decrypt(ciphertext, sentinal)

        except Exception as e:
            print("Failed to decrypt the message: " + str(e))

    # Sign the message using our private key
    def sign(self, message):
        try:
            message_hash = SHA512.new(message.encode('utf-8'))

            self.debug_print("Signing the message:")
            self.debug_print("Message to be hashed: " + message)
            self.debug_print("Hash of the message: " + message_hash.hexdigest())

            signer = PKCS1_v1_5_Signature.new(self.rsa_key)
            signature = b64encode(signer.sign(message_hash))
            return signature.decode('utf-8')

        except Exception as e:
            print("Failed to sign the message: " + str(e))

    # Sign the data, that is hashed, with our private key.
    def sign_data(self, data):
        message = self.get_data_uniq_string(data)        
        return self.sign(message)

    # Verify the signature, based on the message, public key and signature.
    def verify(self, message, public_key, signature):
        try:
            signature = b64decode( signature.encode('utf-8') )
            key = RSA.importKey(public_key)
            h = SHA512.new(message.encode('utf-8'))
            verifier = PKCS1_v1_5_Signature.new(key)
            
            self.debug_print("Message to verify: " + message)
            self.debug_print("Hash of the message: " + h.hexdigest())
            
            return verifier.verify(h, signature)

        except Exception as e:
            print("CRYPTO: " + str(e))

    # Verify the signature, based on the data, public key and signature.
    def verify_data(self, data, public_key, signature):
        message = self.get_data_uniq_string(data)
        return self.verify(message, public_key, signature)

    #######################################################
    # PING / PONG Message packets                         #
    #######################################################

    # A ping request is send to all the nodes that are connected
    def send_ping(self):
        self.send_to_nodes(self.create_message( {'_type': 'ping', 'timestamp': time.time(), 'id': self.id} ))

    # A pong request is only send to the node that has send the ping request
    def send_pong(self, node, timestamp):
        node.send(self.create_message( {'_type': 'pong', 'timestamp': timestamp, 'timestamp_node': time.time(), 'id': self.id} ))

    # With a ping message, return a pong message to the node
    def received_ping(self, node, data):
        self.send_pong(node, data['timestamp']) # Moet weer aan!

    # Got message back based on our ping message, check the latency of the node!
    def received_pong(self, node, data):
        latency = time.time() - data['timestamp']
        print("Received pong message with latence " + str(latency))

    #######################################################
    # DISCOVERY                                           #
    #######################################################

    # TODO: Improve discovery information that is send back by the nodes.
    def send_discovery(self):
        self.send_to_nodes(self.create_message({'_type': 'discovery', 'id': self.id, 'timestamp': time.time() }))

    def send_discovery_answer(self, node, data):
        nodes = []
        for n in self.nodes_inbound:
            nodes.append({'id': n.id, 'ip': n.host, 'port': n.main_node.port, 'connection': 'inbound'})
        for n in self.nodes_outbound:
            nodes.append({'id': n.id, 'ip': n.host, 'port': n.port, 'connection': 'outbound'})

        node.send(self.create_message({'id': data['id'], '_type': 'discovery_answer', 'timestamp': data['timestamp'], 'nodes': nodes}))

    # Got a discovery request, send back a discover_anwser_message with my details
    # and relay it to the other hosts, when I got the answers from them  send it thourgh
    # This means i need to administer these message
    #
    def received_discovery(self, node, data):
        if data['id'] in self.discovery_messages:
            self.debug_print("discovery_message: message already received, so not sending it")

        else:
            self.debug_print("discovery_message: process message")
            self.discovery_messages[data['id']] = node
            self.send_discovery_answer(node, data)
            self.send_to_nodes(self.create_message({'_type': 'discovery', 'id': data['id'], 'timestamp': data['timestamp']}), [node])

    def received_discovery_answer(self, node, data):
        if data['id'] in self.discovery_messages: # needs to be relayed
            self.send_discovery_answer(self.discovery_messages[data['id']], data)

        else:
            if ( data['id'] == self.id ):
                self.debug_print("discovery_message_answer: This is for me!: " + str(data) + ":" + str(time.time()-data['timestamp']))

            else:
                self.debug_print("unknwon state!")
