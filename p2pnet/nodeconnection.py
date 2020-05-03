#######################################################################################################################
# Author: Maurice Snoeren <macsnoeren(at)gmail.com>                                                                   #
# Version: 0.1 beta (use at your own risk)                                                                            #
#                                                                                                                     #
# NodeConnection                                                                                                      #
#######################################################################################################################
import socket
import sys
import time
import threading
import random
import hashlib

class NodeConnection(threading.Thread):
    """Implements the connection that is made with a node. Both inbound and outbound nodes are created with this class.
       Events are send when data is coming from the node Messages could be sent to this node."""

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
