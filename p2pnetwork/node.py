import socket
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

    def __init__(self, host, port, id=None, callback=None, max_connections=0):
        """Create instance of a Node. If you want to implement the Node functionality with a callback, you should 
           provide a callback method. It is preferred to implement a new node by extending this Node class. 
            host: The host name or ip address that is used to bind the TCP/IP server to.
            port: The port number that is used to bind the TCP/IP server to.
            id: (optional) This id will be associated with the node. When not given a unique ID will be created.
            callback: (optional) The callback that is invokes when events happen inside the network.
            max_connections: (optional) limiting the maximum nodes that are able to connect to this node."""
        super(Node, self).__init__()

        # When this flag is set, the node will stop and close
        self.terminate_flag = threading.Event()

        # Server details, host (or ip) to bind to and the port
        self.host = host
        self.port = port

        # Events are send back to the given callback
        self.callback = callback

        # Nodes that have established a connection with this node
        self.nodes_inbound = []  # Nodes that are connect with us N->(US)

        # Nodes that this nodes is connected to
        self.nodes_outbound = []  # Nodes that we are connected to (US)->N

        # A list of nodes that should be reconnected to whenever the connection was lost
        self.reconnect_to_nodes = []

        # Create a unique ID for each node if the ID is not given.
        if id == None:
            self.id = self.generate_id()

        else:
            self.id = str(id) # Make sure the ID is a string!

        # Start the TCP/IP server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.init_server()

        # Message counters to make sure everyone is able to track the total messages
        self.message_count_send = 0
        self.message_count_recv = 0
        self.message_count_rerr = 0
        
        # Connection limit of inbound nodes (nodes that connect to us)
        self.max_connections = max_connections

        # Debugging on or off!
        self.debug = False

    @property
    def all_nodes(self):
        """Return a list of all the nodes, inbound and outbound, that are connected with this node."""
        return self.nodes_inbound + self.nodes_outbound

    def debug_print(self, message):
        """When the debug flag is set to True, all debug messages are printed in the console."""
        if self.debug:
            print("DEBUG (" + self.id + "): " + message)

    def generate_id(self):
        """Generates a unique ID for each node."""
        id = hashlib.sha512()
        t = self.host + str(self.port) + str(random.randint(1, 99999999))
        id.update(t.encode('ascii'))
        return id.hexdigest()

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

    def send_to_nodes(self, data, exclude=[], compression='none'):
        """ Send a message to all the nodes that are connected with this node. data is a python variable which is
            converted to JSON that is send over to the other node. exclude list gives all the nodes to which this
            data should not be sent.
            TODO: When sending was not successfull, the user is not notified."""
        self.message_count_send = self.message_count_send + 1
        for n in self.nodes_inbound:
            if n in exclude:
                self.debug_print("Node send_to_nodes: Excluding node in sending the message")
            else:
                self.send_to_node(n, data, compression)

        for n in self.nodes_outbound:
            if n in exclude:
                self.debug_print("Node send_to_nodes: Excluding node in sending the message")
            else:
                self.send_to_node(n, data, compression)

    def send_to_node(self, n, data, compression='none'):
        """ Send the data to the node n if it exists."""
        self.message_count_send = self.message_count_send + 1
        if n in self.nodes_inbound or n in self.nodes_outbound:
            n.send(data, compression=compression)

        else:
            self.debug_print("Node send_to_node: Could not send the data, node is not found!")

    def connect_with_node(self, host, port, reconnect=False):
        """ Make a connection with another node that is running on host with port. When the connection is made, 
            an event is triggered outbound_node_connected. When the connection is made with the node, it exchanges
            the id's of the node. First we send our id and then we receive the id of the node we are connected to.
            When the connection is made the method outbound_node_connected is invoked. If reconnect is True, the
            node will try to reconnect to the code whenever the node connection was closed. The method returns
            True when the node is connected with the specific host."""

        if host == self.host and port == self.port:
            print("connect_with_node: Cannot connect with yourself!!")
            return False

        # Check if node is already connected with this node!
        for node in self.nodes_outbound:
            if node.host == host and node.port == port:
                print("connect_with_node: Already connected with this node (" + node.id + ").")
                return True

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.debug_print("connecting to %s port %s" % (host, port))
            sock.connect((host, port))

            # Basic information exchange (not secure) of the id's of the nodes!
            sock.send((self.id + ":" + str(self.port)).encode('utf-8')) # Send my id and port to the connected node!
            connected_node_id = sock.recv(4096).decode('utf-8') # When a node is connected, it sends its id!

            # Cannot connect with yourself
            if self.id == connected_node_id:
                print("connect_with_node: You cannot connect with yourself?!")
                sock.send("CLOSING: Already having a connection together".encode('utf-8'))
                sock.close()
                return True

            # Fix bug: Cannot connect with nodes that are already connected with us!
            #          Send message and close the socket.
            for node in self.nodes_inbound:
                if node.host == host and node.id == connected_node_id:
                    print("connect_with_node: This node (" + node.id + ") is already connected with us.")
                    sock.send("CLOSING: Already having a connection together".encode('utf-8'))
                    sock.close()
                    return True

            thread_client = self.create_new_connection(sock, connected_node_id, host, port)
            thread_client.start()

            self.nodes_outbound.append(thread_client)
            self.outbound_node_connected(thread_client)

            # If reconnection to this host is required, it will be added to the list!
            if reconnect:
                self.debug_print("connect_with_node: Reconnection check is enabled on node " + host + ":" + str(port))
                self.reconnect_to_nodes.append({
                    "host": host, "port": port, "tries": 0
                })

            return True

        except Exception as e:
            self.debug_print("TcpServer.connect_with_node: Could not connect with node. (" + str(e) + ")")
            return False

    def disconnect_with_node(self, node):
        """Disconnect the TCP/IP connection with the specified node. It stops the node and joins the thread.
           The node will be deleted from the nodes_outbound list. Before closing, the method 
           node_disconnect_with_outbound_node is invoked."""
        if node in self.nodes_outbound:
            self.node_disconnect_with_outbound_node(node)
            node.stop()

        else:
            self.debug_print("Node disconnect_with_node: cannot disconnect with a node with which we are not connected.")

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

    def reconnect_nodes(self):
        """This method checks whether nodes that have the reconnection status are still connected. If not
           connected these nodes are started again."""
        for node_to_check in self.reconnect_to_nodes:
            found_node = False
            self.debug_print("reconnect_nodes: Checking node " + node_to_check["host"] + ":" + str(node_to_check["port"]))

            for node in self.nodes_outbound:
                if node.host == node_to_check["host"] and node.port == node_to_check["port"]:
                    found_node = True
                    node_to_check["trials"] = 0 # Reset the trials
                    self.debug_print("reconnect_nodes: Node " + node_to_check["host"] + ":" + str(node_to_check["port"]) + " still running!")

            if not found_node: # Reconnect with node
                node_to_check["trials"] += 1
                if self.node_reconnection_error(node_to_check["host"], node_to_check["port"], node_to_check["trials"]):
                    self.connect_with_node(node_to_check["host"], node_to_check["port"]) # Perform the actual connection

                else:
                    self.debug_print("reconnect_nodes: Removing node (" + node_to_check["host"] + ":" + str(node_to_check["port"]) + ") from the reconnection list!")
                    self.reconnect_to_nodes.remove(node_to_check)

    def run(self):
        """The main loop of the thread that deals with connections from other nodes on the network. When a
           node is connected it will exchange the node id's. First we receive the id of the connected node
           and secondly we will send our node id to the connected node. When connected the method
           inbound_node_connected is invoked."""
        while not self.terminate_flag.is_set():  # Check whether the thread needs to be closed
            try:
                self.debug_print("Node: Wait for incoming connection")
                connection, client_address = self.sock.accept()

                self.debug_print("Total inbound connections:" + str(len(self.nodes_inbound)))
                # When the maximum connections is reached, it disconnects the connection 
                if self.max_connections == 0 or len(self.nodes_inbound) < self.max_connections:
                    
                    # Basic information exchange (not secure) of the id's of the nodes!
                    connected_node_port = client_address[1] # backward compatibilty
                    connected_node_id   = connection.recv(4096).decode('utf-8')
                    if ":" in connected_node_id:
                        (connected_node_id, connected_node_port) = connected_node_id.split(':') # When a node is connected, it sends it id!
                    connection.send(self.id.encode('utf-8')) # Send my id to the connected node!

                    thread_client = self.create_new_connection(connection, connected_node_id, client_address[0], connected_node_port)
                    thread_client.start()

                    self.nodes_inbound.append(thread_client)
                    self.inbound_node_connected(thread_client)

                else:
                    self.debug_print("New connection is closed. You have reached the maximum connection limit!")
                    connection.close()
            
            except socket.timeout:
                self.debug_print('Node: Connection timeout!')

            except Exception as e:
                raise e

            self.reconnect_nodes()

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

    def node_disconnected(self, node):
        """While the same nodeconnection class is used, the class itself is not able to
           determine if it is a inbound or outbound connection. This function is making
           sure the correct method is used."""
        self.debug_print("node_disconnected: " + node.id)

        if node in self.nodes_inbound:
            del self.nodes_inbound[self.nodes_inbound.index(node)]
            self.inbound_node_disconnected(node)

        if node in self.nodes_outbound:
            del self.nodes_outbound[self.nodes_outbound.index(node)]
            self.outbound_node_disconnected(node)

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

    def node_reconnection_error(self, host, port, trials):
        """This method is invoked when a reconnection error occurred. The node connection is disconnected and the
           flag for reconnection is set to True for this node. This function can be overidden to implement your
           specific logic to take action when a lot of trials have been done. If the method returns True, the
           node will try to perform the reconnection. If the method returns False, the node will stop reconnecting
           to this node. The node will forever tries to perform the reconnection."""
        self.debug_print("node_reconnection_error: Reconnecting to node " + host + ":" + str(port) + " (trials: " + str(trials) + ")")
        return True

    def __str__(self):
        return 'Node: {}:{}'.format(self.host, self.port)

    def __repr__(self):
        return '<Node {}:{} id: {}>'.format(self.host, self.port, self.id)
