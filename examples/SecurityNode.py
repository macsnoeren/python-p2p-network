#######################################################################################################################
# Author: Maurice Snoeren                                                                                             #
# Version: 0.1 beta (use at your own risk)                                                                            #
#                                                                                                                     #
# SecurityNode is just a trial to implement the Node class with an application. The SecurityNode is a node that       #
# create a security network in which data is encrypted and decrypted for the users that are connected.                #
# It uses JSON formatted data to send to and from the nodes.
#######################################################################################################################
import time
import json
from p2pnet import Node

class SecurityNode (Node):

    # Python class constructor
    def __init__(self, host, port):
        super(SecurityNode, self).__init__(host, port, None)

        self.discovery_messages = {}

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
                    self.dprint("p2p_event_node_message: message type unknown: " + connected_node.id + ": " + str(data))

        except Exception as e:
            self.main_node.debug_print("NodeConnection: Data could not be parsed (%s) (%s)" % (message, str(e)))
       
    def node_disconnect_with_outbound_node(self, connected_node):
        print("node wants to disconnect with oher outbound node: " + connected_node.id)
        
    def node_request_to_stop(self):
        print("node is requested to stop!")
        self.send_to_nodes("")

    ## Extra application specific implementation!

    # Creates a string message from the data that is provided!
    def create_message(self, data):
        data['_mcs'] = self.message_count_send
        data['_mcr'] = self.message_count_recv
        return json.dumps(data, separators=(',', ':'))

    # Perform some check of the message
    def check_message(self, data):
        return True

    def send_message(self, message):
        self.send_to_nodes(self.create_message({ "message": message }))

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
            self.dprint("discovery_message: message already received, so not sending it")

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


         # Obsolete, it uses JSON, while the user of the module could decide whether to use JSON.
            #message = json.dumps(data, separators=(',', ':')) + "-TSN"
            #self.sock.sendall(message.encode('utf-8'))

             # Obsolete code that pinned down the user of the module to use JSON!
                    #try:
                    #    data = json.loads(message)
                    #
                    #except Exception as e:
                    #    self.main_node.debug_print("NodeConnection: Data could not be parsed (%s) (%s)" % (line, str(e)))
                    #
