__title__ = 'python-p2p-network'
__author__ = 'Maurice Snoeren'
__license__ = "GNU 3.0"

import socket
import sys
import json
import time
import threading
import random
import hashlib


class Node(threading.Thread):

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
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.init_server()

        self.message_count_send = 0;
        self.message_count_recv = 0;

        # Debugging on or off!
        self.debug = False

    @property
    def all_nodes(self):
        # Get the all connected nodes
        return self.nodesIn + self.nodesOut

    def debug_print(self, message):
        if self.debug:
            print("DEBUG PRINT: " + message)

    # Creates the TCP/IP socket and bind is to the ip and port
    def init_server(self):
        print("Initialisation of the TcpServer on port: " + str(self.port) + " on node (" + self.id + ")")
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
                self.event_node_inbound_closed(n)

                if self.callback is not None:
                    self.callback("NODEINBOUNDCLOSED", self, n, {})

                n.join()
                del self.nodesIn[self.nodesIn.index(n)]

        for n in self.nodesOut:
            if n.terminate_flag.is_set():
                self.event_node_outbound_closed(n)

                if self.callback is not None:
                    self.callback("NODEOUTBOUNDCLOSED", self, n, {})

                n.join()
                del self.nodesOut[self.nodesIn.index(n)]

    def create_message(self, data):
        self.message_count_send = self.message_count_send + 1
        data['_mcs'] = self.message_count_send
        data['_mcr'] = self.message_count_recv

        return data

    # Send a message to all the nodes that are connected with this node.
    # data is a python variable which is converted to JSON that is send over to the other node.
    # exclude list gives all the nodes to which this data should not be sent.
    def send_to_nodes(self, data, exclude=[]):
        for n in self.nodesIn:
            if n in exclude:
                self.debug_print("TcpServer.send2nodes: Excluding node in sending the message")
            else:
                self.send_to_node(n, data)

        for n in self.nodesOut:
            if n in exclude:
                self.debug_print("TcpServer.send2nodes: Excluding node in sending the message")
            else:
                self.send_to_node(n, data)

    # Send the data to the node n if it exists.
    # data is a python variable which is converted to JSON that is send over to the other node.
    def send_to_node(self, n, data):
        self.delete_closed_connections()
        if n in self.nodesIn or n in self.nodesOut:
            try:
                n.send(self.create_message(data))

            except Exception as e:
                self.debug_print("TcpServer.send2node: Error while sending data to the node (" + str(e) + ")");
        else:
            self.debug_print("TcpServer.send2node: Could not send the data, node is not found!")

    # Make a connection with another node that is running on host with port.
    # When the connection is made, an event is triggered CONNECTEDWITHNODE.
    def connect_with_node(self, host, port):
        print("connect_with_node(" + host + ", " + str(port) + ")")
        if host == self.host and port == self.port:
            print("connect_with_node: Cannot connect with yourself!!")

        # Check if node is already connected with this node!
        for node in self.nodesOut:
            if node.get_host() == host and node.get_port() == port:
                print("connect_with_node: Already connected with this node.")
                return True

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.debug_print("connecting to %s port %s" % (host, port))
            sock.connect((host, port))

            thread_client = self.create_new_connection(sock, (host, port), self.callback)
            thread_client.start()
            self.nodesOut.append(thread_client)
            self.event_connected_with_node(thread_client)

            if self.callback is not None:
                self.callback("CONNECTEDWITHNODE", self, thread_client, {})

            self.print_connections()

        except Exception as e:
            self.debug_print("TcpServer.connect_with_node: Could not connect with node. (" + str(e) + ")")

    # Disconnect with a node. It sends a last message to the node!
    def disconnect_with_node(self, node):
        if node in self.nodesOut:
            node.send(self.create_message({"type": "message", "message": "Terminate connection"}))
            node.stop()
            node.join()  # When this is here, the application is waiting and waiting
            del self.nodesOut[self.nodesOut.index(node)]

    # When this function is executed, the thread will stop!
    def stop(self):
        self.terminate_flag.set()

    # This method can be overrided when a different nodeconnection is required!
    def create_new_connection(self, connection, client_address, callback):
        return NodeConnection(self, connection, client_address, callback)

    # This method is required for the Thead function and is called when it is started.
    # This function implements the main loop of this thread.
    def run(self):
        while not self.terminate_flag.is_set():  # Check whether the thread needs to be closed
            try:
                self.debug_print("TcpServerNode: Wait for incoming connection")
                connection, client_address = self.sock.accept()

                # TODO: Startup first communication in which the details of the node is communicated

                thread_client = self.create_new_connection(connection, client_address, self.callback)
                thread_client.start()
                self.nodesIn.append(thread_client)

                self.event_node_connected(thread_client)

                if self.callback is not None:
                    self.callback("NODECONNECTED", self, thread_client, {})

            except socket.timeout:
                pass

            except Exception as e:
                raise e

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

        # For visuals!
        self.send_visuals("node-closed", {"host": self.host, "port": self.port})

    # Started to implement the events, so this class can be extended with a better class
    # In the event a callback can be called!

    # node is the node thread that is running to get information and send information to.
    def event_node_connected(self, node):
        self.debug_print("event_node_connected: " + node.getName())

        # For visuals!
        self.send_visuals("node-connection-from", {"host": node.host, "port": node.port})

    def event_connected_with_node(self, node):
        self.debug_print("event_node_connected: " + node.getName())

        # For visuals!
        self.send_visuals("node-connection-to", {"host": node.host, "port": node.port})

    def event_node_inbound_closed(self, node):
        self.debug_print("event_node_inbound_closed: " + node.getName())

        # For visuals!
        self.send_visuals("node-connection-from-closed", {"host": node.host, "port": node.port})

    def event_node_outbound_closed(self, node):
        self.debug_print("event_node_outbound_closed: " + node.getName())

        # For visuals!
        self.send_visuals("node-connection-to-closed", {"host": node.host, "port": node.port})

    def event_node_message(self, node, data):
        self.debug_print("event_node_message: " + node.getName() + ": " + str(data))


class NodeConnection(threading.Thread):
    __doc__ = '''
    Class NodeConnection:
    Implements the connection that is made with a node.
    Both inbound and outbound nodes are created with this class.
    Events are send when data is coming from the node
    Messages could be sent to this node.
    '''

    def __init__(self, node_server, sock, client_address, callback):
        super(NodeConnection, self).__init__()

        self.host = client_address[0]
        self.port = client_address[1]
        self.nodeServer = node_server
        self.sock = sock
        self.clientAddress = client_address
        self.callback = callback
        self.terminate_flag = threading.Event()

        # Variable for parsing the incoming json messages
        self.buffer = ""

        id = hashlib.md5()
        t = self.host + str(self.port) + str(random.randint(1, 99999999))
        id.update(t.encode('ascii'))
        self.id = id.hexdigest()

        self.nodeServer.debug_print(
            "NodeConnection.send: Started with client (" + self.id + ") '" + self.host + ":" + str(self.port) + "'")

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    # Send data to the node. The data should be a python variable
    # This data is converted into json and send.
    def send(self, data):
        try:
            message = json.dumps(data, separators=(',', ':')) + "-TSN";
            self.sock.sendall(message.encode('utf-8'))

            # For visuals!
            self.nodeServer.send_visuals("node-send", data)

        except Exception as e:
            self.nodeServer.debug_print("NodeConnection.send: Unexpected error:", sys.exc_info()[0])
            self.nodeServer.debug_print("Exception: " + e)
            self.terminate_flag.set()

    @staticmethod
    def check_message(self, data):
        return True

    def get_id(self):
        # TODO: Remove this, are redundant
        return self.id

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
                self.nodeServer.debug_print("Connection timeout")

            except Exception as e:
                self.terminate_flag.set()
                self.nodeServer.debug_print("NodeConnection: Socket has been terminated (%s)" % line)
                self.nodeServer.debug_print(e)

            if line != "":
                try:
                    self.buffer += str(line.decode('utf-8'))

                except Exception as e:
                    print("NodeConnection: Decoding line error")

                # Get the messages
                index = self.buffer.find("-TSN")
                while index > 0:
                    message = self.buffer[0:index]
                    self.buffer = self.buffer[index + 4::]

                    try:
                        data = json.loads(message)
                        print(data)

                    except Exception as e:
                        print("NodeConnection: Data could not be parsed (%s) (%s)" % (line, str(e)))

                    if self.check_message(data):
                        self.nodeServer.message_count_recv = self.nodeServer.message_count_recv + 1
                        self.nodeServer.event_node_message(self, data)

                        if self.callback is not None:
                            self.callback("NODEMESSAGE", self.nodeServer, self, data)

                        # For visuals!
                        self.nodeServer.send_visuals("node-receive", data)

                    else:
                        self.nodeServer.send_visuals("node-error", {"error": "failed check"})
                        self.nodeServer.debug_print("-------------------------------------------")
                        self.nodeServer.debug_print("Message is damaged and not correct:\nMESSAGE:")
                        self.nodeServer.debug_print(message)
                        self.nodeServer.debug_print("DATA:")
                        self.nodeServer.debug_print(str(data))
                        self.nodeServer.debug_print("-------------------------------------------")

                    index = self.buffer.find("-TSN")

            time.sleep(0.01)

        self.sock.settimeout(None)
        self.sock.close()
        self.nodeServer.debug_print("NodeConnection: Stopped")
