#######################################################################################################################
# AVANS - BLOCKCHAIN - MINOR MAD                                                                                      #
#                                                                                                                     #
# Author: Maurice Snoeren                                                                                             #
# Version: 0.1 beta (use at your own risk)                                                                            #
#                                                                                                                     #
# TcpServerNode creates a TCP/IP server on the port you have given. It accepts incoming nodes and put these into its  #
# internal datastructure. When nodes disconnect, the nodes are removed. Events are generated when nodes are connected #
# , when nodes leave and when nodes have data. Furthermore, this class is able to connect to other nodes. Sending     #
# data to these nodes is easy as well. The datastructure is up to you and how you implement the protocol to form the  #
# decentralized peer-to-peer network. This class is at you disposal to use within your code to speed up the           #
# development.                                                                                                        #
#######################################################################################################################

import socket
import sys
import json
import time
import threading
import pprint
import random
import hashlib
import re

#######################################################################################################################
# TCPServer Class #####################################################################################################
#######################################################################################################################

# Class Node
# Implements a node that is able to connect to other nodes and is able to accept connections from other nodes.
# After instantiation, the node creates a TCP/IP server with the given port.
#
class Node(threading.Thread):

    # Python class constructor
    def __init__(self, host, port, callback):
        super(Node, self).__init__()

        # When this flag is set, the node will stop and close
        self.terminate_flag = threading.Event()

        # Server details, host (or ip) to bind to and the port
        self.host = host
        self.port = port

        # Events are send back to the given callback
        self.callback = callback

        # Nodes that have established a connection with this node
        self.nodesIn = []  # Nodes that are connect with us N->(US)->N

        # Nodes that this nodes is connected to
        self.nodesOut = []  # Nodes that we are connected to (US)->N

        # Create a unique ID for each node.
        id = hashlib.md5()
        t = self.host + str(self.port) + str(random.randint(1, 99999999))
        id.update(t.encode('ascii'))
        self.id = id.hexdigest()

        # Start the TCP/IP server
        self.init_server()

    # Creates the TCP/IP socket and bind is to the ip and port
    def init_server(self):
        print("Initialisation of the TcpServer on port: " + str(self.port) + " on node (" + self.id + ")")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.settimeout(10.0)
        self.sock.listen(1)

    # Print the nodes with this node is connected to. It makes two lists. One for the nodes that have established
    # a connection with this node and one for the node that this node has made connection with.
    def print_connections(self):
        print("Connection status:")
        print("- Total nodes connected with us: %d" % len(self.nodesIn))
        print("- Total nodes connected to     : %d" % len(self.nodesOut))

    # Misleading function name, while this function checks whether the connected nodes have been terminated
    # by the other host. If so, clean the array list of the nodes.
    # When a connection is closed, an event is send NODEINBOUNDCLOSED or NODEOUTBOUNDCLOSED
    def delete_closed_connections(self):
        for n in self.nodesIn:
            if n.terminate_flag.is_set():
                self.callback("NODEINBOUNDCLOSED", self, n, {})
                n.join()
                del self.nodesIn[self.nodesIn.index(n)]

        for n in self.nodesOut:
            if n.terminate_flag.is_set():
                self.callback("NODEOUTBOUNDCLOSED", self, n, {})
                n.join()
                del self.nodesOut[self.nodesIn.index(n)]

    # Send a message to all the nodes that are connected with this node.
    # data is a python variable which is converted to JSON that is send over to the other node.
    # exclude list gives all the nodes to which this data should not be sent.
    def send_to_nodes(self, data, exclude = []):
        for n in self.nodesIn:
            if n in exclude:
                print("TcpServer.send2nodes: Excluding node in sending the message")
            else:
                self.send_to_node(n, data)

        for n in self.nodesOut:
            if n in exclude:
                print("TcpServer.send2nodes: Excluding node in sending the message")
            else:
                self.send_to_node(n, data)

    # Send the data to the node n if it exists.
    # data is a python variabele which is converted to JSON that is send over to the other node.
    def send_to_node(self, n, data):
        self.delete_closed_connections()
        if n in self.nodesIn or n in self.nodesOut:
            try:
                n.send(data)
            except:
                print("TcpServer.send2node: Error while sending data to the node");
        else:
            print("TcpServer.send2node: Could not send the data, node is not found!")

    # Make a connection with another node that is running on host with port.
    # When the connection is made, an event is triggered CONNECTEDWITHNODE.
    def connect_with_node(self, host, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("connecting to %s port %s" % (host, port))
            sock.connect((host, port))

            thread_client = NodeConnection(self, sock, (host, port), self.callback)
            thread_client.start()
            self.nodesOut.append(thread_client)
            self.callback("CONNECTEDWITHNODE", self, thread_client, {})
            self.print_connections()

        except:
            print("TcpServer.connect_with_node: Could not connect with node.")

    # Disconnect with a node. It sends a last message to the node!
    def disconnect_with_node(self, node):
        if node in self.nodesOut:
            node.stop()
            node.send({"type": "message", "message": "Terminate connection"})
            node.join() # When this is here, the application is waiting and waiting
            del self.nodesOut[self.nodesOut.index(node)]

    # When this function is executed, the thread will stop!
    def stop(self):
        self.terminate_flag.set()

    # This method is required for the Thead function and is called when it is started.
    # This function implements the main loop of this thread.
    def run(self):
        while not self.terminate_flag.is_set():  # Check whether the thread needs to be closed
            try:
                print("Wait for connection")
                connection, client_address = self.sock.accept()
                thread_client = NodeConnection(self, connection, client_address, self.callback)
                thread_client.start()
                self.nodesIn.append(thread_client)

                self.callback("NODECONNECTED", self, thread_client, {})

            except socket.timeout:
                pass

            except:
                raise

            time.sleep(0.01)

        print("TcpServer stopping...")
        for t in self.nodesIn:
            t.stop()

        for t in self.nodesOut:
            t.stop()

        time.sleep(1)

        for t in self.nodesIn:
            t.join()

        for t in self.nodesOut:
            t.join()

        self.sock.close()
        print("TcpServer stopped")

#######################################################################################################################
# NodeConnection Class ###############################################################################################
#######################################################################################################################

# Class NodeConnection
# Implements the connection that is made with a node.
# Both inbound and outbound nodes are created with this class.
# Events are send when data is coming from the node
# Messages could be sent to this node.


class NodeConnection(threading.Thread):

    # Python constructor
    def __init__(self, nodeServer, sock, clientAddress, callback):
        super(NodeConnection, self).__init__()

        self.host = clientAddress[0]
        self.port = clientAddress[1]
        self.nodeServer = nodeServer
        self.sock = sock
        self.clientAddress = clientAddress
        self.callback = callback
        self.terminate_flag = threading.Event()

        # Variable for parsing the incoming json messages
        self.buffer = ""
        self.message_count = 0;

        id = hashlib.md5()
        t = self.host + str(self.port) + str(random.randint(1, 99999999))
        id.update(t.encode('ascii'))
        self.id = id.hexdigest()

        print("NodeConnection.send: Started with client (" + self.id + ") '" + self.host + ":" + str(self.port) + "'")

    # Send data to the node. The data should be a python variabele
    # This data is converted into json and send.
    def send(self, data):
        self.message_count = self.message_count + 1
        data['_mc'] = self.message_count
        try:
            message = json.dumps(data, separators=(',', ':')) + "-TSN";
            self.sock.sendall(message.encode('utf-8'))

        except:
            print("NodeConnection.send: Unexpected error:", sys.exc_info()[0])
            self.terminate_flag.set()

    def get_message_count(self):
        return self.message_count

    # Stop the node client. Please make sure you join the thread.
    def stop(self):
        self.terminate_flag.set()

    # Required to implement the Thread. This is the main loop of the node client.
    def run(self):

        # Timeout, so the socket can be closed when it is dead!
        self.sock.settimeout(10.0)

        while not self.terminate_flag.is_set(): # Check whether the thread needs to be closed
            line = ""
            try:
                line = self.sock.recv(4096) # the line ends with -TSN\n

            except socket.timeout:
                pass

            except:
                self.terminate_flag.set()
                print("NodeConnection: Socket has been terminated (%s)" % line)

            if line != "":
                self.buffer += str(line.decode('utf-8'))

                # Get the messages
                index = self.buffer.find("-TSN")
                while ( index > 0 ):
                    message = self.buffer[0:index]
                    self.buffer = self.buffer[index+4::]
                    index = self.buffer.find("-TSN")
                    try:
                        obj = json.loads(message)
                        self.callback("NODEMESSAGE", self.nodeServer, self, obj)
                    except:
                        print("NodeConnection: Data could not be parsed (%s)" % line)

            time.sleep(0.01)

        self.sock.settimeout(None)
        self.sock.close()
        print("NodeConnection: Stopped")

    def get_message(self):
        print("TESTING")

#######################################################################################################################
# Example usage of Node ###############################################################################################
#######################################################################################################################
#
# from TcpServerNode import Node
#
# node = None # global variable
#
# def callbackNodeEvent(event, node, other, data):
#    print("Event Node 1 (" + node.id + "): %s: %s" % (event, data))
#    node.send2nodes({"thank": "you"})
#
# node = Node('localhost', 10000, callbackNodeEvent)
#
# node.start()
#
# node.connect_with_node('12.34.56.78', 20000)
#
# server.terminate_flag.set() # Stopping the thread
#
# node.send2nodes({"type": "message", "message": "test"})
#
# while ( 1 ):
#    time.sleep(1)
#
# node.stop()
#
# node.join()
#
#
# END OF FILE