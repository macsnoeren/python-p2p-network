# python-p2p-network
Basic peer-to-peer TCP/IP network node to implement decentralized peer-to-peer network applications. Use at your own risk! Created for my students following the Avans Minor MAD - Blockchain course.

## Description
TcpServerNode creates a TCP/IP server on the port you have given. It accepts incoming nodes and put these into its  
internal datastructure. When nodes disconnect, the nodes are removed. Events are generated when nodes are connected 
, when nodes leave and when nodes have data. Furthermore, this class is able to connect to other nodes. Sending     
data to these nodes is easy as well. The datastructure is up to you and how you implement the protocol to form the  
decentralized peer-to-peer network. This class is at you disposal to use within your code to speed up the           
development.                                                                                                        

## New node
n = Node(host, port, callback_node_event)

Example: n = Node('localhost', 10000, callback_node_event)

Creates a node on port 1000 and sends all the events to the function callbackNodeEvent.

## Connecting with other nodes
To become part of the p2p network, it is required to connect to some other nodes that already form the network.

node.connect_with_node(ip/host, port)

Example: node.connect_with_node(11.22.33.44, 20000)

## Callback function to capture events
def callbackNodeEvent(event, node, other, data):

node, the server node that is assiocated with this event.
other, the node that the server node is connected with
data, when available this holds the data as python data variable

Event callback is called by the node. node is the object that generated the event. other is the node that caused the event. The following even types exist:
+ NODEINBOUNDCLOSED – Connected node closed
+ NODEOUTBOUNDCLOSED – Connection with node closed
+ CONNECTEDWITHNODE – Connection with node established
+ NODECONNECTED – Node connected with the server
+ NODEMESSAGE – Message from a connected node (data available)

## Example
###test_tcp_server_node_callback.py

An example that uses the callback functionality that is provided
by the TcpServerNode class. TcpServerNode also enables you to
extend the class and implement your own event in stead of 
callbacks. This is another example.

```python
from TcpServerNode import Node

node = None # global variable

def callback_node_event(event, node, other, data):
   print("Event Node 1 (" + node.id + "): %s: %s" % (event, data))
   node.send_to_nodes({"thank": "you"})

node = Node('localhost', 10000, callback_node_event)

node.start()

node.connect_with_node('12.34.56.78', 20000)

#node.terminate_flag.set() # Stopping the thread

node.send_to_nodes({"type": "message", "message": "test"})

while True:
   time.sleep(1)

node.stop()

```

###MyPeer2PeerNode.py

This example shows how to extend the TcpServerNode class in order
to create your own implementation of a peer-to-peer network node.
This implementation is preffered, while callbacks is a bit 
more complex to implement large applications.

```python
import TcpServerNode

class MyPeer2PeerNode (TcpServerNode.Node):

    def __init__(self, host, port):
        super(MyPeer2PeerNode, self).__init__(host, port, None)

        print("MyPeer2PeerNode: Started")

    # Method override, implement here your own functionality!
    def event_node_connected(self, node):
        print("p2p_event_node_connected: " + node.getName())

    def event_connected_with_node(self, node):
        print("p2p_event_node_connected: " + node.getName())

    def event_node_inbound_closed(self, node):
        print("p2p_event_node_inbound_closed: " + node.getName())

    def event_node_outbound_closed(self, node):
        print("p2p_event_node_outbound_closed: " + node.getName())

    # If a message comes in, determines what to do!
    def event_node_message(self, node, data):
        print("p2p_event_node_message: " + node.getName() + ": " + str(data))
````

###test_avans_node.py

This example shows how to use a peer-to-peer implementation. In
this case the AvansNode class is used, that implements a simple
transaction system and some node functionality, like ping, pong
and discovery. From the main application you can simply connect
with the network and send transaction, which are then validated
by the nodes and send to the other nodes.

```python
import time
from AvansNode import AvansNode

node_p2p1 = AvansNode('localhost', 1000)
node_p2p2 = AvansNode('localhost', 2000)
node_p2p3 = AvansNode('localhost', 3000)
node_p2p4 = AvansNode('localhost', 4000)

node_p2p1.start()
node_p2p2.start()
node_p2p3.start()
node_p2p4.start()

# All nodes connect to node 1
node_p2p2.connect_with_node('localhost', 1000)
node_p2p3.connect_with_node('localhost', 1000)
node_p2p4.connect_with_node('localhost', 1000)

node_p2p1.print_connections()

time.sleep(5)

# A transaction is created and sent to the other nodes.
# The nodes should check their blockchain to validate that
# Maurice has 1000 AvansCoins. If oké, they can sent it
# to their connected nodes.
node_p2p1.send_transacation("Maurice", "Diederich", 1000)

time.sleep(10)

node_p2p1.stop()
node_p2p2.stop()
node_p2p3.stop()
node_p2p4.stop()

print("main stopped")
````
