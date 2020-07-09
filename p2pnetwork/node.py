import socket
import sys
import time
import threading
import random
import hashlib

from p2pnetwork.nodeconnection import NodeConnection

"""
Author: Maurice Snoeren <macsnoeren(at)gmail.com>
Version: 0.3 beta (use at your own risk)
Date: 7-5-2020

Python package p2pnet for implementing decentralized peer-to-peer network applications

TODO: Variabele to limit the number of connected nodes.
TODO: Also create events when things go wrong, like a connection with a node has failed.
"""

class Node(threading.Thread):
    """Implements a node that is able to connect to other nodes and is able to accept connections from other nodes.
    After instantiation, the node creates a TCP/IP server with the given port.

    Create instance of a Node. If you want to implement the Node functionality with a callback, you should 
    provide a callback method. It is preferred to implement a new node by extending this Node class. 
      host: The host name or ip address that is used to bind the TCP/IP server to.
      port: The port number that is used to bind the TCP/IP server to.
      callback: (optional) The callback that is invokes when events happen inside the network
               def node_callback(event, main_node, connected_node, data):
                 event: The event string that has happened.
                 main_node: The main node that is running all the connections with the other nodes.
                 connected_node: Which connected node caused the event.
                 data: The data that is send by the connected node."""

    def __init__(self, host, port, callback=None):
        """Create instance of a Node. If you want to implement the Node functionality with a callback, you should 
           provide a callback method. It is preferred to implement a new node by extending this Node class. 
            host: The host name or ip address that is used to bind the TCP/IP server to.
            port: The port number that is used to bind the TCP/IP server to.
            callback: (optional) The callback that is invokes when events happen inside the network."""
        super(Node, self).__init__()

        # When this flag is set, the node will stop and close
        self.terminate_flag = threading.Event()

        # Server details, host (or ip) to bind to and the port
        self.host = host
        self.port = port

        # Events are send back to the given callback
        self.callback = callback

        # Nodes that have established a connection with this node
        self.nodes_inbound = []  # Nodes that are connect with us N->(US)->N

        # Nodes that this nodes is connected to
        self.nodes_outbound = []  # Nodes that we are connected to (US)->N

        # Create a unique ID for each node.
        # TODO: A fixed unique ID is required for each node, node some random is created, need to think of it.
        id = hashlib.sha512()
        t = self.host + str(self.port) + str(random.randint(1, 99999999))
        id.update(t.encode('ascii'))
        self.id = id.hexdigest()

        # Start the TCP/IP server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.init_server()

        # Message counters to make sure everyone is able to track the total messages
        self.message_count_send = 0
        self.message_count_recv = 0
        self.message_count_rerr = 0

        # Debugging on or off!
        self.debug = False

    @property
    def all_nodes(self):
        """Return a list of all the nodes, inbound and outbound, that are connected with this node."""
        return self.nodes_inbound + self.nodes_outbound

    def debug_print(self, message):
        """When the debug flag is set to True, all debug messages are printed in the console."""
        if self.debug:
            print("DEBUG: " + message)

    def init_server(self):
        """Initialization of the TCP/IP server to receive connections. It binds to the given host and port."""
        print("Initialisation of the Node on port: " + str(self.port) + " on node (" + self.id + ")")
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.settimeout(10.0)
        self.sock.listen(1)

    def print_connections(self):
        """Prints the connection overview of the node. How many inbound and outbound connections have been made."""
        print("Node connection overview:")
        print("- Total nodes connected with us: %d" % len(self.nodes_inbound))
        print("- Total nodes connected to     : %d" % len(self.nodes_outbound))

    def delete_closed_connections(self):
        """Misleading function name, while this function checks whether the connected nodes have been terminated
           by the other host. If so, clean the array list of the nodes. When a connection is closed, an event is 
           send node_message or outbound_node_disconnected."""
        for n in self.nodes_inbound:
            if n.terminate_flag.is_set():
                self.inbound_node_disconnected(n)
                n.join()
                del self.nodes_inbound[self.nodes_inbound.index(n)]

        for n in self.nodes_outbound:
            if n.terminate_flag.is_set():
                self.outbound_node_disconnected(n)
                n.join()
                del self.nodes_outbound[self.nodes_inbound.index(n)]

    def send_to_nodes(self, data, exclude=[]):
        """ Send a message to all the nodes that are connected with this node. data is a python variable which is
            converted to JSON that is send over to the other node. exclude list gives all the nodes to which this
            data should not be sent."""
        self.message_count_send = self.message_count_send + 1
        for n in self.nodes_inbound:
            if n in exclude:
                self.debug_print("Node send_to_nodes: Excluding node in sending the message")
            else:
                self.send_to_node(n, data)

        for n in self.nodes_outbound:
            if n in exclude:
                self.debug_print("Node send_to_nodes: Excluding node in sending the message")
            else:
                self.send_to_node(n, data)

    def send_to_node(self, n, data):
        """ Send the data to the node n if it exists."""
        self.message_count_send = self.message_count_send + 1
        self.delete_closed_connections()
        if n in self.nodes_inbound or n in self.nodes_outbound:
            try:
                n.send(data)

            except Exception as e:
                self.debug_print("Node send_to_node: Error while sending data to the node (" + str(e) + ")")
        else:
            self.debug_print("Node send_to_node: Could not send the data, node is not found!")

    def connect_with_node(self, host, port):
        """ Make a connection with another node that is running on host with port. When the connection is made, 
            an event is triggered outbound_node_connected. When the connection is made with the node, it exchanges
            the id's of the node. First we send our id and then we receive the id of the node we are connected to.
            When the connection is made the method outbound_node_connected is invoked.
            TODO: think wheter we need an error event to trigger when the connection has failed!"""
        if host == self.host and port == self.port:
            print("connect_with_node: Cannot connect with yourself!!")
            return False

        # Check if node is already connected with this node!
        for node in self.nodes_outbound:
            if node.host == host and node.port == port:
                print("connect_with_node: Already connected with this node.")
                return True

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.debug_print("connecting to %s port %s" % (host, port))
            sock.connect((host, port))

            # Basic information exchange (not secure) of the id's of the nodes!
            sock.send(self.id.encode('utf-8')) # Send my id to the connected node!
            connected_node_id = sock.recv(4096).decode('utf-8') # When a node is connected, it sends it id!

            thread_client = self.create_new_connection(sock, connected_node_id, host, port)
            thread_client.start()

            self.nodes_outbound.append(thread_client)
            self.outbound_node_connected(thread_client)

        except Exception as e:
            self.debug_print("TcpServer.connect_with_node: Could not connect with node. (" + str(e) + ")")

    def disconnect_with_node(self, node):
        """Disconnect the TCP/IP connection with the specified node. It stops the node and joins the thread.
           The node will be deleted from the nodes_outbound list. Before closing, the method 
           node_disconnect_with_outbound_node is invoked."""
        if node in self.nodes_outbound:
            self.node_disconnect_with_outbound_node(node)
            node.stop()
            node.join()  # When this is here, the application is waiting and waiting
            del self.nodes_outbound[self.nodes_outbound.index(node)]

        else:
            print("Node disconnect_with_node: cannot disconnect with a node with which we are not connected.")

    def stop(self):
        """Stop this node and terminate all the connected nodes."""
        self.node_request_to_stop()
        self.terminate_flag.set()

    # This method can be overrided when a different nodeconnection is required!
    def create_new_connection(self, connection, id, host, port):
        """When a new connection is made, with a node or a node is connecting with us, this method is used
           to create the actual new connection. The reason for this method is to be able to override the
           connection class if required. In this case a NodeConnection will be instantiated to represent
           the node connection."""
        return NodeConnection(self, connection, id, host, port)

    def run(self):
        """The main loop of the thread that deals with connections from other nodes on the network. When a
           node is connected it will exchange the node id's. First we receive the id of the connected node
           and secondly we will send our node id to the connected node. When connected the method
           inbound_node_connected is invoked."""
        while not self.terminate_flag.is_set():  # Check whether the thread needs to be closed
            try:
                self.debug_print("Node: Wait for incoming connection")
                connection, client_address = self.sock.accept()
                
                # Basic information exchange (not secure) of the id's of the nodes!
                connected_node_id = connection.recv(4096).decode('utf-8') # When a node is connected, it sends it id!
                connection.send(self.id.encode('utf-8')) # Send my id to the connected node!

                thread_client = self.create_new_connection(connection, connected_node_id, client_address[0], client_address[1])
                thread_client.start()

                self.nodes_inbound.append(thread_client)

                self.inbound_node_connected(thread_client)
                
            except socket.timeout:
                self.debug_print('Node: Connection timeout!')

            except Exception as e:
                raise e

            time.sleep(0.01)

        print("Node stopping...")
        for t in self.nodes_inbound:
            t.stop()

        for t in self.nodes_outbound:
            t.stop()

        time.sleep(1)

        for t in self.nodes_inbound:
            t.join()

        for t in self.nodes_outbound:
            t.join()

        self.sock.settimeout(None)   
        self.sock.close()
        print("Node stopped")

    def outbound_node_connected(self, node):
        """This method is invoked when a connection with a outbound node was successfull. The node made
           the connection itself."""
        self.debug_print("outbound_node_connected: " + node.id)
        if self.callback is not None:
            self.callback("outbound_node_connected", self, node, {})

    def inbound_node_connected(self, node):
        """This method is invoked when a node successfully connected with us."""
        self.debug_print("inbound_node_connected: " + node.id)
        if self.callback is not None:
            self.callback("inbound_node_connected", self, node, {})

    def inbound_node_disconnected(self, node):
        """This method is invoked when a node, that was previously connected with us, is in a disconnected
           state."""
        self.debug_print("inbound_node_disconnected: " + node.id)
        if self.callback is not None:
            self.callback("inbound_node_disconnected", self, node, {})

    def outbound_node_disconnected(self, node):
        """This method is invoked when a node, that we have connected to, is in a disconnected state."""
        self.debug_print("outbound_node_disconnected: " + node.id)
        if self.callback is not None:
            self.callback("outbound_node_disconnected", self, node, {})

    def node_message(self, node, data):
        """This method is invoked when a node send us a message."""
        self.debug_print("node_message: " + node.id + ": " + str(data))
        if self.callback is not None:
            self.callback("node_message", self, node, data)

    def node_disconnect_with_outbound_node(self, node):
        """This method is invoked just before the connection is closed with the outbound node. From the node
           this request is created."""
        self.debug_print("node wants to disconnect with oher outbound node: " + node.id)
        if self.callback is not None:
            self.callback("node_disconnect_with_outbound_node", self, node, {})

    def node_request_to_stop(self):
        """This method is invoked just before we will stop. A request has been given to stop the node and close
           all the node connections. It could be used to say goodbey to everyone."""
        self.debug_print("node is requested to stop!")
        if self.callback is not None:
            self.callback("node_request_to_stop", self, {}, {})

    def __str__(self):
        return 'Node: {}:{}'.format(self.host, self.port)

    def __repr__(self):
        return '<Node {}:{} id: {}>'.format(self.host, self.port, self.id)
