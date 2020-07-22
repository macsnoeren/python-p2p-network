# Python implementation of a peer-to-peer decentralized network
This project provides a basic and simple peer-to-peer decentralized network classes (framework) to build your own network. Basic functionality of the nodes and the connection to and from these  nodes has been implemented. Application specific functionality is up to you to implement yourself. The intention of the module is to provide a good basis, without specific implementation, so everyone is really free to implement like they would like to do.

You can use the project to implement a peer-to-peer decentralized network application, like Bitcoin or file sharing applications. I have used this software to provide my students, during a technical introduction to Blockchain, basic functionality. So, they were able to focus on how they would like to implement the Blockchain functionality and protocols. Without some direction from my side. Some of the students have used the code base to implement their application in C# or C++, for example. That is the freedom I would like to give to everyone.

To install the package for you to use (https://pypi.org/project/p2pnetwork/):
````
pip install p2pnetwork
````
See p2pnetwork in action https://github.com/macsnoeren/python-p2p-secure-node. This SecureNode implements a node that communicates securely between the nodes. A good example how a specific application is created by using this framework.

# Evolution of the software
While I started this project in the year 2018, it was mainly focussed to provide my students some software to be able to implement a peer-to-peer decentralized network. Without the hassle to design and create everything by themselves. While I did not have any experience with Python yet and there was not much time, I put everything in place in a very large pace. One of my students was annoyed by the camelCase programming style, while the Python community uses PEP-8. So, Christian decided to help me out and structured the software to the PEP style. Two years later, Samuel decided to clean up the code and create a real module from it. From then, I decided to jump in again and made the proposed changes, while maintaining the intention of the software: basic peer-to-peer decentralized functionality without specific implementation of protocols, so the programmer is able to freely implement these on their own. I still think that the software is a good basis and already have a new goal to use this software for a decentralized security application.

On github I was wandering around and noticed that others contributed as well to the code. No pull request, but still nice things. Therefore, I have not transformed the Python software to a package to be available on pypi.org. Anyway, thanks for all the collaboration and I hope you will still help me out and others will join as well. It is possible to develop more specific applications by other modules and classes. Adding these to the repository will create a nice overview about the possibilities of these kind of applications.

# Design
At first glance, peer-to-peer decentralized network applications are complex and difficult. While you need to provide some networking functionality on application level, the architecture is really simple. You have a network of the "same" nodes. The "same" means the same application (or an application that implements the same protocol).

Nodes are connected with each other. This means that each node provides a TCP/IP server on a specific port to provide inbound nodes to connect. The same node is able to connect to other nodes; called outbound nodes. When a node has a lot of connections with nodes in the network, the node will get most likely the required messages. You are able to send a message over the TCP/IP channel to the connected (inbound and outbound) nodes. How they react to the messages is in your hands. When you would like to implement discovery, meaning to see which nodes are connected within the network and see if you would like to connect to those, you need to relay this message to the other nodes connected to you. Note that you need to make sure that the messages will not echo around, but that you keep track which messages you have received.

How to optimize these node connections depend on what you would like to solve. When providing file sharing, you would like to have a lot of connections when nodes have a large bandwith. However, when you are running Bitcoin, you would like to have your connections spread over the world to minimize the single identity problem.

## You have two options
Because of my lack of Python experience, I started off with an event scheme that is used within C. When an event occurred, a callback function is called with the necessary variables to be able to process the request and implement the network protocol you desire.

However, having a class and being able to extend the class with your own implementation is much nicer. Therefore, I started to change the code towards this new scheme. While maintaining the callback functionality, while my students where already busy. I could not let them be victim from my changes.

So, you have therefore two options:
1. Implement your p2p application by extending Node and NodeConnection classes
2. Implement your p2p application with one callback function

Examples have been provided by the package. These files can be found in the examples directory. My preference is to extend the classes, so we could build on each other's ideas in the future.

## Option 1: Implement your p2p application by extending Node and NodeConnection classes
This option is preferred and gives the most flexibility. To implement your p2p network application, you could also extend the classes Node and/or NodeConnection. At least you need to extend the class Node with your own implementation. To implement the application specific functionality, you override the methods that represent the events. You are able to create different classes and methods to provide the code to implement the application protocol and functionality. While more files are involved an example is given by the next sections. 

### Extend class Node
Extending the class Node is easy. Make sure you override at least all the events. Whenever, you extend the class, it is not possible to use the callback function anymore. See the example below. You can also check the file examples/MyOwnPeer2PeerNode.py.

````python
from p2pnetwork.node import Node

class MyOwnPeer2PeerNode (Node):
    # Python class constructor
    def __init__(self, host, port):
        super(MyOwnPeer2PeerNode, self).__init__(host, port, None)

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

    # OPTIONAL
    # If you need to override the NodeConection as well, you need to
    # override this method! In this method, you can initiate
    # you own NodeConnection class.
    def create_new_connection(self, connection, id, host, port):
        return MyOwnNodeConnection(self, connection, id, host, port)
````
### Extend class NodeConnection
The NodeConnection class only hold the TCP/IP connection with the other node, to manage the different connection to and from the main node. It does not implement application specific elements. Mostly, you will only need to extend the Node class. However, when you would like to create your own NodeConnection class you can do this. Make sure that you override ````create_new_connection(self, connection, id, host, port)```` in the class Node, to make sure you initiate your own NodeConnection class. The example below shows some example.

````python
from p2pnetwork.node import Node

class MyOwnPeer2PeerNode (Node):
    # Python class constructor
    def __init__(self, host, port):
        super(MyOwnPeer2PeerNode, self).__init__(host, port, None)

    # Override event functions...

    # Override this method to initiate your own NodeConnection class.
    def create_new_connection(self, connection, id, host, port):
        return MyOwnNodeConnection(self, connection, id, host, port)
````

````python
from p2pnetwork.nodeconnection import NodeConnection

class MyOwnNodeConnection (NodeConnection):
    # Python class constructor
     def __init__(self, main_node, sock, id, host, port):
        super(MyOwnNodeConnection, self).__init__(main_node, sock, id, host, port)

    # Check yourself what you would like to change and override! See the 
    # documentation
````

### Using your new classes
You have extended the Node class and maybe also the NodeConnection class. The next aspect it to use your new p2p network application by using these classes. You create a new python file and start using your classes. See the example below. Check the file example/my_own_p2p_application.py for this implementation.

````python
import sys
import time

from MyOwnPeer2PeerNode import MyOwnPeer2PeerNode

node = MyOwnPeer2PeerNode("127.0.0.1", 10001)
time.sleep(1)

# Do not forget to start your node!
node.start()
time.sleep(1)

# Connect with another node, otherwise you do not create any network!
node.connect_with_node('127.0.0.1', 10002)
time.sleep(2)

# Example of sending a message to the nodes (dict).
node.send_to_nodes({"message": "Hi there!"})

time.sleep(5) # Create here your main loop of the application

node.stop()
````

## Option 2: Implement your p2p application with one callback function
While this is the least preferable method, you are in the lead! You need to create a callback method and spin off the Node from the module p2pnet. All events that happen within the network will be transferred to the callback function. All application specific functionality can be implemented within this callback and the methods provided by the classes Node and NodeConnection. See below an example of an implementation. You can check the file examples/my_own_p2p_application_callback.py for the full implementation.

````python
import time
from p2pnetwork.node import Node

# node_callback
#  event         : event name
#  node          : the node (Node) that holds the node connections
#  connected_node: the node (NodeConnection) that is involved
#  data          : data that is send by the node (could be empty)
def node_callback(event, node, connected_node, data):
    try:
        if event != 'node_request_to_stop': # node_request_to_stop does not have any connected_node, while it is the main_node that is stopping!
            print('Event: {} from main node {}: connected node {}: {}'.format(event, node.id, connected_node.id, data))

    except Exception as e:
        print(e)

# The main node that is able to make connections to other nodes
# and accept connections from other nodes on port 8001.
node = Node("127.0.0.1", 10001, node_callback)

# Do not forget to start it, it spins off a new thread!
node.start()
time.sleep(1)

# Connect to another node, otherwise you do not have any network.
node.connect_with_node('127.0.0.1', 10002)
time.sleep(2)

# Send some message to the other nodes
node.send_to_nodes('{"message": "hoi from node 1"}')

time.sleep(5) # Replace this sleep with your main loop!

# Gracefully stop the node.
node.stop()
````

## Events that can occur

### outbound_node_connected
The node connects with another node - ````node.connect_with_node('127.0.0.1', 8002)```` - and the connection is successful. While the basic functionality is to exchange the node id's, no user data is involved.

### inbound_node_connected
Another node has made a connection with this node and the connection is successful. While the basic functionality is to exchange the node id's, no user data is involved.

### outbound_node_disconnected
A node, to which we had made a connection in the past, is disconnected.

### inbound_node_disconnected
A node, that had made a connection with us in the past, is disconnected.

### node_message
A node - ```` connected_node ```` - sends a message. At this moment the basic functionality expects JSON format. It tries to decode JSON when the message is received. If it is not possible, the message is rejected.

### node_disconnect_with_outbound_node
The application actively wants to disconnect the outbound node, a node with which we had made a connection in the past. You could send some last message to the node, that you are planning to disconnect, for example.

### node_request_to_stop
The main node, also the application, is stopping itself. Note that the variable connected_node is empty, while there is no connected node involved.

# Debugging

When things go wrong, you could enable debug messages of the Node class. The class shows these messages in the console and shows all the details of what happens within the class. To enable debugging for a node, use the code example below.

````python
node = Node("127.0.0.1", 10001)
node.debug = True
````

# Unit testing

Several unit tests have been implemented to make sure all the functionality of the provided classes are working correctly. To run these tests, you can use the following code:

````bash
$ python setup.py test
````

# Examples

Examples are available in the github repository of this project: https://github.com/macsnoeren/python-p2p-network. All examples can be found in the directory examples.

# Node and NodeConnection class                                       

See the Python documentation for all the details of these classes.

# Show case: SecureNode
As a show case, I have created the SecureNode class that extends the Node class. This node uses JSON, hashing and signing to communicate between the nodes. My main thought with this secure node is to be able to exchange data securely with each other and give others permissions to read the data, for example. You are the owner of your data! Anyway, some project that I am currently working on. See the documentation of this specific class file.

````python
import sys
import time

from p2pnetwork.securenode import SecureNode

node = SecureNode("127.0.0.1", 10001)
time.sleep(1)

node.start()
````
An example node that uses SecureNode class is found in the example directory on github: ````secure_node.py````.
