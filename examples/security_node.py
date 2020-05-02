#######################################################################################################################
# Author: Maurice Snoeren                                                                                             #
# Version: 0.1 beta (use at your own risk)                                                                            #
#                                                                                                                     #
# This example uses the SecurityNode to implement a security node and the functionality of this security node.        #
# As example all commands are from the commandline                                                                    #
#######################################################################################################################

import sys
import time
sys.path.insert(0, '..') # Import the files where the modules are located

from SecurityNode import SecurityNode

security_node = SecurityNode("127.0.0.1", 9001)
security_node_o1 = SecurityNode("127.0.0.1", 9002) # This is the main network node!
security_node_o2 = SecurityNode("127.0.0.1", 9003)

security_node.start()
security_node_o1.start()
security_node_o2.start()
time.sleep(1)

security_node.connect_with_node('127.0.0.1', 9002)
security_node_o2.connect_with_node('127.0.0.1', 9002)

time.sleep(2)

security_node.debug = True

running = True
while running:
    print("Commands: message, ping, discovery, stop")
    s = input("Please type a command:")
    if s == "stop":
        running = False

    elif s == "message":
        security_node.send_message("Hoi daar!")

    elif s == "ping":
        security_node.send_ping()

    elif s == "discovery":
        security_node.send_discovery()

    else:
        print("Command not understood '" + s + "'")   

security_node.stop()
security_node_o1.stop()
security_node_o2.stop()

