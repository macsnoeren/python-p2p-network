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
```python
from TcpServerNode import Node

node = None # global variable

def callback_node_event(event, node, other, data):
   print("Event Node 1 (" + node.id + "): %s: %s" % (event, data))
   node.send_to_nodes({"thank": "you"})

node = Node('localhost', 10000, callback_node_event)

node.start()

node.connect_with_node('12.34.56.78', 20000)

node.terminate_flag.set() # Stopping the thread

node.send_to_nodes({"type": "message", "message": "test"})

while True:
   time.sleep(1)

node.stop()

node.join()
```
