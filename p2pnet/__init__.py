__title__ = 'python-p2p-network'
__author__ = 'Maurice Snoeren'
__license__ = "GNU 3.0"

import socket
import sys
import time
import threading
import random
import hashlib

class Node(threading.Thread):
    __doc__ = '''
    Class Node:
    Implements a node that is able to connect to other nodes and is able to accept connections from other nodes.
    After instantiation, the node creates a TCP/IP server with the given port.
    '''
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
        self.messgaE_count_rerr = 0

        # Debugging on or off!
        self.debug = False

    # Get the all connected nodes
    @property
    def all_nodes(self):
        return self.nodes_inbound + self.nodes_outbound

    def debug_print(self, message):
        if self.debug:
            print("DEBUG PRINT: " + message)

    # Creates the TCP/IP socket and bind is to the ip and port
    def init_server(self):
        print("Initialisation of the Node on port: " + str(self.port) + " on node (" + self.id + ")")
        self.sock.bind((self.host, self.port))
        self.sock.settimeout(10.0)
        self.sock.listen(1)

    # Print the nodes with this node is connected to. It makes two lists. One for the nodes that have established
    # a connection with this node and one for the node that this node has made connection with.
    def print_connections(self):
        print("Node connection overview:")
        print("- Total nodes connected with us: %d" % len(self.nodes_inbound))
        print("- Total nodes connected to     : %d" % len(self.nodes_outbound))

    # Misleading function name, while this function checks whether the connected nodes have been terminated
    # by the other host. If so, clean the array list of the nodes.
    # When a connection is closed, an event is send node_message or outbound_node_disconnected
    def delete_closed_connections(self):
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

    # Obsolete, while this defines that we use JSON formatted message, it is up to the programmer how to deal with this!
    # Will be deleted in the future!
    #def create_message(self, data):
    #    data['_mcs'] = self.message_count_send
    #    data['_mcr'] = self.message_count_recv
    #    return data

    # Send a message to all the nodes that are connected with this node.
    # data is a python variable which is converted to JSON that is send over to the other node.
    # exclude list gives all the nodes to which this data should not be sent.
    def send_to_nodes(self, data, exclude=[]):
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

    # Send the data to the node n if it exists.
    # data is a python variable which is converted to JSON that is send over to the other node.
    def send_to_node(self, n, data):
        self.message_count_send = self.message_count_send + 1
        self.delete_closed_connections()
        if n in self.nodes_inbound or n in self.nodes_outbound:
            try:
                #Obsolete while this uses JSON format, the user of the module decide what to do!
                #n.send(self.create_message(data))
                n.send(data)

            except Exception as e:
                self.debug_print("Node send_to_node: Error while sending data to the node (" + str(e) + ")")
        else:
            self.debug_print("Node send_to_node: Could not send the data, node is not found!")

    # Make a connection with another node that is running on host with port.
    # When the connection is made, an event is triggered outbound_node_connected.
    # TODO: think wheter we need an error event to trigger when the connection has failed!
    def connect_with_node(self, host, port):
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
            connected_node_id = str(sock.recv(4096).decode('utf-8')) # When a node is connected, it sends it id!

            thread_client = self.create_new_connection(sock, connected_node_id, host, port)
            thread_client.start()

            self.nodes_outbound.append(thread_client)
            self.outbound_node_connected(thread_client)

        except Exception as e:
            self.debug_print("TcpServer.connect_with_node: Could not connect with node. (" + str(e) + ")")

    # Disconnect with a node. You could sens a last message to the node!
    def disconnect_with_node(self, node):
        if node in self.nodes_outbound:
            self.node_disconnect_with_outbound_node(node)
            node.stop()
            node.join()  # When this is here, the application is waiting and waiting
            del self.nodes_outbound[self.nodes_outbound.index(node)]

        else:
            print("Node disconnect_with_node: cannot disconnect with a node with which we are not connected.")

    # When this function is executed, the thread will stop!
    def stop(self):
        self.node_request_to_stop()
        self.terminate_flag.set()

    # This method can be overrided when a different nodeconnection is required!
    def create_new_connection(self, connection, id, host, port):
        return NodeConnection(self, connection, id, host, port)

    # This method is required for the Thread function and is called when it is started.
    # This function implements the main loop of this thread.

    def run(self):
        while not self.terminate_flag.is_set():  # Check whether the thread needs to be closed
            try:
                self.debug_print("Node: Wait for incoming connection")
                connection, client_address = self.sock.accept()
                
                # Basic information exchange (not secure) of the id's of the nodes!
                connected_node_id = str(connection.recv(4096).decode('utf-8')) # When a node is connected, it sends it id!
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

        self.sock.close()
        print("Node stopped")

    # Started to implement the events, so this class can be extended with a better class
    # In the event a callback can be called!

    # node is the node thread that is running to get information and send information to.
    def outbound_node_connected(self, node):
        self.debug_print("outbound_node_connected: " + node.id)
        if self.callback is not None:
            self.callback("outbound_node_connected", self, node, {})

    def inbound_node_connected(self, node):
        self.debug_print("inbound_node_connected: " + node.id)
        if self.callback is not None:
            self.callback("inbound_node_connected", self, node, {})

    def inbound_node_disconnected(self, node):
        self.debug_print("inbound_node_disconnected: " + node.id)
        if self.callback is not None:
            self.callback("inbound_node_disconnected", self, node, {})

    def outbound_node_disconnected(self, node):
        self.debug_print("outbound_node_disconnected: " + node.id)
        if self.callback is not None:
            self.callback("outbound_node_disconnected", self, node, {})

    def node_message(self, node, data):
        self.debug_print("node_message: " + node.id + ": " + str(data))
        if self.callback is not None:
            self.callback("node_message", self, node, data)

    def node_disconnect_with_outbound_node(self, node):
        self.debug_print("node wants to disconnect with oher outbound node: " + node.id)
        if self.callback is not None:
            self.callback("node_disconnect_with_outbound_node", self, node, {})

    def node_request_to_stop(self):
        self.debug_print("node is requested to stop!")
        if self.callback is not None:
            self.callback("node_request_to_stop", self, {}, {})

    def __str__(self):
        return 'Node: {}:{}'.format(self.host, self.port)

    def __repr__(self):
        return '<Node {}:{} id: {}>'.format(self.host, self.port, self.id)


class NodeConnection(threading.Thread):
    __doc__ = '''
    Class NodeConnection:
    Implements the connection that is made with a node. Both inbound and outbound nodes are created with this class.
    Events are send when data is coming from the node Messages could be sent to this node.
    '''

    def __init__(self, main_node, sock, id, host, port):
        super(NodeConnection, self).__init__()

        self.host = host
        self.port = port
        self.main_node = main_node
        self.sock = sock
        self.terminate_flag = threading.Event()

        # Variable for parsing the incoming json messages
        self.buffer = ""

        # The id of the connected node
        self.id = id

        self.main_node.debug_print(
            "NodeConnection.send: Started with client (" + self.id + ") '" + self.host + ":" + str(self.port) + "'")

    # Send data to the node. The data should be a python variable
    # This data is converted into json and send. When you want to create a message
    # to be send, please use self.create_message(data)
    def send(self, data):
        try:
            # Obsolete, it uses JSON, while the user of the module could decide whether to use JSON.
            #message = json.dumps(data, separators=(',', ':')) + "-TSN"
            #self.sock.sendall(message.encode('utf-8'))
            data = data + "-TSN"
            self.sock.sendall(data.encode('utf-8'))

        except Exception as e:
            self.main_node.debug_print("NodeConnection.send: Unexpected error:", sys.exc_info()[0])
            self.main_node.debug_print("Exception: " + str(e))
            self.terminate_flag.set()

    # This method should be implemented by yourself! We do not know when the message is
    # correct.
    # def check_message(self, data):
    #         return True

    # Stop the node client. Please make sure you join the thread.
    def stop(self):
        self.terminate_flag.set()

    # Required to implement the Thread. This is the main loop of the node client.
    def run(self):
        # Timeout, so the socket can be closed when it is dead!
        self.sock.settimeout(10.0)          
 
        while not self.terminate_flag.is_set():  # Check whether the thread needs to be closed
            line = ""
            try:
                line = self.sock.recv(4096)  # the line ends with -TSN\n

            except socket.timeout:
                self.main_node.debug_print("NodeConnection: timeout")

            except Exception as e:
                self.terminate_flag.set()
                self.main_node.debug_print("NodeConnection: Socket has been terminated (%s)" % line)
                self.main_node.debug_print(e)

            if line != "":
                try:
                    self.buffer += str(line.decode('utf-8'))

                except Exception as e:
                    print("NodeConnection: Decoding line error | " + str(e))

                # Get the messages
                index = self.buffer.find("-TSN")
                while index > 0:
                    message = self.buffer[0:index]
                    self.buffer = self.buffer[index + 4::]

                    self.main_node.message_count_recv += 1
                    self.main_node.node_message(self, message)

                    # Obsolete code that pinned down the user of the module to use JSON!
                    #try:
                    #    data = json.loads(message)
                    #
                    #except Exception as e:
                    #    self.main_node.debug_print("NodeConnection: Data could not be parsed (%s) (%s)" % (line, str(e)))
                    #
                    #if self.check_message(data):
                    #    self.main_node.message_count_recv += 1
                    #    self.main_node.node_message(self, data)
                    #
                    #else:
                    #    self.main_node.messgaE_count_rerr += 1
                    #    self.main_node.debug_print("-------------------------------------------")
                    #    self.main_node.debug_print("Message is damaged and not correct:\nMESSAGE:")
                    #    self.main_node.debug_print(message)
                    #    self.main_node.debug_print("DATA:")
                    #    self.main_node.debug_print(str(data))
                    #    self.main_node.debug_print("-------------------------------------------")

                    index = self.buffer.find("-TSN")

            time.sleep(0.01)

        self.sock.settimeout(None)
        self.sock.close()
        self.main_node.debug_print("NodeConnection: Stopped")

    def __str__(self):
        return 'NodeConnection: {}:{} <-> {}:{} ({})'.format(self.main_node.host, self.main_node.port, self.host, self.port, self.id)

    def __repr__(self):
        return '<NodeConnection: Node {}:{} <-> Connection {}:{}>'.format(self.main_node.host, self.main_node.port, self.host, self.port)
