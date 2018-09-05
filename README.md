# python-p2p-network
Basic peer-to-peer TCP/IP network node to implement decentralized peer-to-peer network applications.

## Description
TcpServerNode creates a TCP/IP server on the port you have given. It accepts incoming nodes and put these into its  
internal datastructure. When nodes disconnect, the nodes are removed. Events are generated when nodes are connected 
, when nodes leave and when nodes have data. Furthermore, this class is able to connect to other nodes. Sending     
data to these nodes is easy as well. The datastructure is up to you and how you implement the protocol to form the  
decentralized peer-to-peer network. This class is at you disposal to use within your code to speed up the           
development.                                                                                                        

## Example
from TcpServerNode import Node

node = None # global variable

def callbackNodeEvent(event, node, other, data):
   print("Event Node 1 (" + node.id + "): %s: %s" % (event, data))
   node.send2nodes({"thank": "you"})

node = Node('localhost', 10000, callbackNodeEvent)

node.start()

node.connectWithNode('12.34.56.78', 20000)

server.terminate_flag.set() # Stopping the thread

node.send2nodes({"type": "message", "message": "test"})

while ( 1 ):
   time.sleep(1)

node.stop()

node.join()
