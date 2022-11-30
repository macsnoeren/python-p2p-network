import socket
import time
import threading
import json
import zlib, bz2, lzma, base64

"""
Author : Maurice Snoeren <macsnoeren(at)gmail.com>
Version: 0.3 beta (use at your own risk)
Date: 7-5-2020

Python package p2pnet for implementing decentralized peer-to-peer network applications
"""


class NodeConnection(threading.Thread):
    """The class NodeConnection is used by the class Node and represent the TCP/IP socket connection with another node. 
       Both inbound (nodes that connect with the server) and outbound (nodes that are connected to) are represented by
       this class. The class contains the client socket and hold the id information of the connecting node. Communication
       is done by this class. When a connecting node sends a message, the message is relayed to the main node (that created
       this NodeConnection in the first place).
       
       Instantiates a new NodeConnection. Do not forget to start the thread. All TCP/IP communication is handled by this 
       connection.
        main_node: The Node class that received a connection.
        sock: The socket that is assiociated with the client connection.
        id: The id of the connected node (at the other side of the TCP/IP connection).
        host: The host/ip of the main node.
        port: The port of the server of the main node."""

    def __init__(self, main_node, sock, id, host, port):
        """Instantiates a new NodeConnection. Do not forget to start the thread. All TCP/IP communication is handled by this connection.
            main_node: The Node class that received a connection.
            sock: The socket that is assiociated with the client connection.
            id: The id of the connected node (at the other side of the TCP/IP connection).
            host: The host/ip of the main node.
            port: The port of the server of the main node."""

        self.host = host
        self.port = port
        self.main_node = main_node
        self.sock = sock
        self.terminate_flag = threading.Event()

        # The id of the connected node
        self.id = str(id)  # Make sure the ID is a string

        # End of transmission character for the network streaming messages.
        self.EOT_CHAR = 0x04.to_bytes(1, 'big')

        # Indication that the message has been compressed
        self.COMPR_CHAR = 0x02.to_bytes(1, 'big')

        # Datastore to store additional information concerning the node.
        self.info = {}

        # Use socket timeout to determine problems with the connection
        self.sock.settimeout(10.0)

        self.main_node.debug_print(
            "NodeConnection: Started with client (" + self.id + ") '" + self.host + ":" + str(self.port) + "'")
        super(NodeConnection, self).__init__()

    def compress(self, data, compression):
        """Compresses the data given the type. It is used to provide compression to lower the network traffic in case of
           large data chunks. It stores the compression type inside the data, so it can be easily retrieved."""

        self.main_node.debug_print(self.id + ":compress:" + compression)
        self.main_node.debug_print(self.id + ":compress:input: " + str(data))

        compressed = data

        try:
            if compression == 'zlib':
                compressed = base64.b64encode(zlib.compress(data, 6) + b'zlib')

            elif compression == 'bzip2':
                compressed = base64.b64encode(bz2.compress(data) + b'bzip2')

            elif compression == 'lzma':
                compressed = base64.b64encode(lzma.compress(data) + b'lzma')

            else:
                self.main_node.debug_print(self.id + ":compress:Unknown compression")
                return None

        except Exception as e:
            self.main_node.debug_print("compress: exception: " + str(e))

        self.main_node.debug_print(self.id + ":compress:b64encode:" + str(compressed))
        self.main_node.debug_print(
            self.id + ":compress:compression:" + str(int(10000 * len(compressed) / len(data)) / 100) + "%")

        return compressed

    def decompress(self, compressed):
        """Decompresses the data given the type. It is used to provide compression to lower the network traffic in case of
           large data chunks."""
        self.main_node.debug_print(self.id + ":decompress:input: " + str(compressed))
        compressed = base64.b64decode(compressed)
        self.main_node.debug_print(self.id + ":decompress:b64decode: " + str(compressed))

        try:
            if compressed[-4:] == b'zlib':
                compressed = zlib.decompress(compressed[0:len(compressed) - 4])

            elif compressed[-5:] == b'bzip2':
                compressed = bz2.decompress(compressed[0:len(compressed) - 5])

            elif compressed[-4:] == b'lzma':
                compressed = lzma.decompress(compressed[0:len(compressed) - 4])
        except Exception as e:
            print("Exception: " + str(e))

        self.main_node.debug_print(self.id + ":decompress:result: " + str(compressed))

        return compressed

    def send(self, data, encoding_type='utf-8', compression='none'):
        """Send the data to the connected node. The data can be pure text (str), dict object (send as json) and bytes object.
           When sending bytes object, it will be using standard socket communication. A end of transmission character 0x04 
           utf-8/ascii will be used to decode the packets ate the other node. When the socket is corrupted the node connection
           is closed. Compression can be enabled by using zlib, bzip2 or lzma. When enabled the data is compressed and send to
           the client. This could reduce the network bandwith when sending large data chunks.
           """
        if isinstance(data, str):
            try:
                if compression == 'none':
                    self.sock.sendall(data.encode(encoding_type) + self.EOT_CHAR)
                else:
                    data = self.compress(data.encode(encoding_type), compression)
                    if data != None:
                        self.sock.sendall(data + self.COMPR_CHAR + self.EOT_CHAR)

            except Exception as e:  # Fixed issue #19: When sending is corrupted, close the connection
                self.main_node.debug_print("nodeconnection send: Error sending data to node: " + str(e))
                self.stop()  # Stopping node due to failure

        elif isinstance(data, dict):
            try:
                if compression == 'none':
                    self.sock.sendall(json.dumps(data).encode(encoding_type) + self.EOT_CHAR)
                else:
                    data = self.compress(json.dumps(data).encode(encoding_type), compression)
                    if data != None:
                        self.sock.sendall(data + self.COMPR_CHAR + self.EOT_CHAR)

            except TypeError as type_error:
                self.main_node.debug_print('This dict is invalid')
                self.main_node.debug_print(type_error)

            except Exception as e:  # Fixed issue #19: When sending is corrupted, close the connection
                self.main_node.debug_print("nodeconnection send: Error sending data to node: " + str(e))
                self.stop()  # Stopping node due to failure

        elif isinstance(data, bytes):
            try:
                if compression == 'none':
                    self.sock.sendall(data + self.EOT_CHAR)
                else:
                    data = self.compress(data, compression)
                    if data != None:
                        self.sock.sendall(data + self.COMPR_CHAR + self.EOT_CHAR)

            except Exception as e:  # Fixed issue #19: When sending is corrupted, close the connection
                self.main_node.debug_print("nodeconnection send: Error sending data to node: " + str(e))
                self.stop()  # Stopping node due to failure

        else:
            self.main_node.debug_print('datatype used is not valid plese use str, dict (will be send as json) or bytes')

    def stop(self):
        """Terminates the connection and the thread is stopped. Stop the node client. Please make sure you join the thread."""
        self.terminate_flag.set()

    def parse_packet(self, packet):
        """Parse the packet and determines wheter it has been send in str, json or byte format. It returns
           the according data."""
        if packet.find(self.COMPR_CHAR) == len(packet) - 1:  # Check if packet was compressed
            packet = self.decompress(packet[0:-1])

        try:
            packet_decoded = packet.decode('utf-8')

            try:
                return json.loads(packet_decoded)

            except json.decoder.JSONDecodeError:
                return packet_decoded

        except UnicodeDecodeError:
            return packet

    # Required to implement the Thread. This is the main loop of the node client.
    def run(self):
        """The main loop of the thread to handle the connection with the node. Within the
           main loop the thread waits to receive data from the node. If data is received 
           the method node_message will be invoked of the main node to be processed."""
        buffer = b''  # Hold the stream that comes in!

        while not self.terminate_flag.is_set():
            chunk = b''

            try:
                chunk = self.sock.recv(4096)

            except socket.timeout:
                self.main_node.debug_print("NodeConnection: timeout")

            except Exception as e:
                self.terminate_flag.set()  # Exception occurred terminating the connection
                self.main_node.debug_print('Unexpected error')
                self.main_node.debug_print(e)

            # BUG: possible buffer overflow when no EOT_CHAR is found => Fix by max buffer count or so?
            if chunk != b'':
                buffer += chunk
                eot_pos = buffer.find(self.EOT_CHAR)

                while eot_pos > 0:
                    packet = buffer[:eot_pos]
                    buffer = buffer[eot_pos + 1:]

                    self.main_node.message_count_recv += 1
                    self.main_node.node_message(self, self.parse_packet(packet))

                    eot_pos = buffer.find(self.EOT_CHAR)

            time.sleep(0.01)

        # IDEA: Invoke (event) a method in main_node so the user is able to send a bye message to the node before it is closed?
        self.sock.settimeout(None)
        self.sock.close()
        self.main_node.node_disconnected(
            self)  # Fixed issue #19: Send to main_node when a node is disconnected. We do not know whether it is inbounc or outbound.
        self.main_node.debug_print("NodeConnection: Stopped")

    def set_info(self, key, value):
        self.info[key] = value

    def get_info(self, key):
        return self.info[key]

    def __str__(self):
        return 'NodeConnection: {}:{} <-> {}:{} ({})'.format(self.main_node.host, self.main_node.port, self.host,
                                                             self.port, self.id)

    def __repr__(self):
        return '<NodeConnection: Node {}:{} <-> Connection {}:{}>'.format(self.main_node.host, self.main_node.port,
                                                                          self.host, self.port)

    def __hash__(self):
        return hash(self.main_node.id + self.id)

    def __eq__(self, other):
        return self.main_node == other.main_node and self.id == other.id
