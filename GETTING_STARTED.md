# Getting started with p2pnetwork
This tutorial provides you with a walk through how to use the p2pnetwork framework. If you would like to use this framework, you can use these steps to get familiar with the module. Eventually it is up to you to use and implement your specific details to the p2pnetwork applications.

This example is also available on github: https://github.com/macsnoeren/python-p2p-network-example.git.

## Should I use this module?
**If you would like to create peer-to-peer network applications ... the answer is yes!** The module provides you with all the basic details of peer-to-peer network applications. It starts a node that is able to connect to other nodes and is able to receive connections from other nodes. When running a node, you get all the details using an event based structure. When some node is connecting or sending a message, methods are invokes, so you immediatly can react on it. In other words, implementing your application details. 

Note that it is a framework that provide the basics of a peer-to-peer network application. The basic idea is not to implement application specifics, so the developer is really in the lead. For example, a peer-to-peer network application implements most likely a discovery function. This function discovers the nodes that form the network. You need to implement this on your own. Meaning that you need to design a protocol and implement it within your class.

## Example project
In this tutorial we focus on a peer-to-peer file sharing network application. The application forms a peer-to-peer network and is able to discover other nodes. Nodes share a directory on their computer that hold files to be shared within the network. A node is able to search for a specific file and download the file respectively.

## Step 1: Install the module
To install the package for you to use (https://pypi.org/project/p2pnetwork/):
````
pip install p2pnetwork
````

## Step 2: Create your project
Create a directory on your computer and create two files. The first file is the class that implements the file sharing peer-to-peer network application. This class extends from the Node class of the p2p-network module. The second file is the python executable file that initiates the class and implements a console interface to interact with our file sharing node. When you are ready the directory should like this:
````
FileSharingNode.py
file_sharing_node.py
````
## Step 3: Setup the file sharing class
Open the file ````FileSharingNode.py```` and create the class FileSharingNode that extends from the Node class of the p2pnetwork modules. The code below shows the example.
````python
from p2pnetwork.node import Node

class FileSharingNode (Node):

    def __init__(self, host, port, id=None, callback=None, max_connections=0):
        super(FileSharingNode, self).__init__(host, port, id, callback, max_connections)

    def outbound_node_connected(self, connected_node):
        print("outbound_node_connected: " + connected_node.id)
        
    def inbound_node_connected(self, connected_node):
        print("inbound_node_connected: " + connected_node.id)

    def inbound_node_disconnected(self, connected_node):
        print("inbound_node_disconnected: " + connected_node.id)

    def outbound_node_disconnected(self, connected_node):
        print("outbound_node_disconnected: " + connected_node.id)

    def node_message(self, connected_node, data):
        print("node_message from " + connected_node.id + ": " + str(data))
        
    def node_disconnect_with_outbound_node(self, connected_node):
        print("node wants to disconnect with oher outbound node: " + connected_node.id)
        
    def node_request_to_stop(self):
        print("node is requested to stop!")

````
## Step 4: Setup console application
Open the file ````file_sharing_node.py```` and create a console application that instantiates the ````FileSharingNode.py````.

````python
import sys

from FileSharingNode import FileSharingNode

# The port to listen for incoming node connections
port = 9876 # default

# Syntax file_sharing_node.py port
if len(sys.argv) > 1:
    port = int(sys.argv[1])

# Instantiate the node FileSharingNode, it creates a thread to handle all functionality
node = FileSharingNode("127.0.0.1", port)

# Start the node, if not started it shall not handle any requests!
node.start()

# The method prints the help commands text to the console
def print_help():
    print("stop - Stops the application.")
    print("help - Prints this help text.")

# Implement a console application
command = input("? ")
while ( command != "stop" ):
    if ( command == "help" ):
        print_help()

    command = input("? ")

node.stop()
````
Running this example code results in the following console output:
````
Initialisation of the Node on port: 9876 on node (e5ab15fdf31dcf6f0c4490d5ebb216f6ee8a6f86fca5a33bcbc8b63d7c963b2caf6c46410d5667bcd792fc02d7652e7cb50475d949c45506c6585f059637a449)
? help
stop - Stops the application.
help - Prints this help text.
? stop
node is requested to stop!
Node stopping...
Node stopped
````

From this moment, you have already a bare minimum application that implements the framework p2pnetwork. No application specifics have been coded yet. The node is already listening to incoming connections and able to connect to other nodes at your command. From this point, we will add the required functionality to the application. In order to test this applications, you need to run the application twice on different ports. In this case you could open two terminals and run the following commands:
1. ````python file_sharing_node.py 9876````
2. ````python file_sharing_node.py 9877````

## Step 5: Connect to another node
We are going to add the functionality to connect with another node. In this case, you should spin off in another terminal the application on port 9877: ````file_sharing_node.py 9877````. When the user wants to connect to another node, you need to provide a host/ip and port number. Add the following code to ````file_sharing_node.py````.

````python
....
def connect_to_node(node:FileSharingNode):
    host = input("host or ip of node? ")
    port = int(input("port? "))
    node.connect_with_node(host, port)

# Implement a console application
command = input("? ")
while ( command != "stop" ):
    if ( command == "help" ):
        print_help()
    if ( command == "connect"):
        connect_to_node(node)

    command = input("? ")
....
````
When you run the application and connect to another node, you immediatly see the invoked message of the methods in the ````FileSharingNode.py````. Below the console output of the application. When you connect to another node, it will be placed in the outbound list, because it is an outgoing connection. 
````
$>file_sharing_node.py 9876
Initialisation of the Node on port: 9876 on node (ceccce67f62d2d067bca76901ba3da2028539754b451afa81b0ffe2fcc64e070386f5573ee6cf4da9223202d363c3aeb035b360ad5bd95985e1797e93cd93b28)
? connect
host or ip of node? localhost
port? 9877
outbound_node_connected: df643d3c0063b40fcb0c185a9f39e4743551ef426c9acc0355cb01b04288dd87909f7d2ca74d594b266ee6dd149d8e2b3a82c4ee9584382ec4e91230aad1118d
````
This application running at port 9877 is receives the connection. Therefore, you see an inbound message. The incoming connection from the node is added to the inbound list, because it is a connection with us.
````
$>file_sharing_node.py 9877
Initialisation of the Node on port: 9877 on node (df643d3c0063b40fcb0c185a9f39e4743551ef426c9acc0355cb01b04288dd87909f7d2ca74d594b266ee6dd149d8e2b3a82c4ee9584382ec4e91230aad1118d)
? inbound_node_connected: ceccce67f62d2d067bca76901ba3da2028539754b451afa81b0ffe2fcc64e070386f5573ee6cf4da9223202d363c3aeb035b360ad5bd95985e1797e93cd93b28
````
You already see that you have a lot of control of what happens. Immediatly, you get notified when nodes are connected. Eventually, how nodes are connected is not really important when messages are send to each other.

_work in progress..._