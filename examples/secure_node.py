import sys
import time
sys.path.insert(0, '..')

from p2pnetwork.securenode import SecureNode

"""
Author: Maurice Snoeren
Version: 0.1 beta (use at your own risk)

This example uses the SecureNode to implement a node and the functionality of this security node. The class
SecureNode is provided by the p2pnet package as well.

python secure_node.py <host> <port>
python secure_node.py <port>
"""
host = "127.0.0.1"
port = 8000

if len(sys.argv) > 1:
    port = int(sys.argv[1])

if len(sys.argv) > 2:
    host = sys.argv[1]
    port = int(sys.argv[2])

# Start the SecureNode
node = SecureNode(host, port)

node.start()
node.debug = False
time.sleep(1)

running = True
while running:
    print("Commands: message, ping, discovery, status, connect, stop")
    s = input("Please type a command:")

    if s == "stop":
        running = False

    elif s == "message":
        node.send_message(input("Message to send:"))

    elif s == "ping":
        node.send_ping()

    elif s == "discovery":
        node.send_discovery()

    elif s == "status":
        node.print_connections()

    elif ( s == "connect"):
        host = input("host: ")
        port = int(input("port: "))
        node.connect_with_node(host, port)

    else:
        print("Command not understood '" + s + "'")   

node.stop()
