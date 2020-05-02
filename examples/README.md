# Example peer-to-peer decentralized applications
This directory contains several examples and one real project of a peer-to-peer decentralized application. It is really nice to play around with decentralized applications. The following examples have been provided:
1. Implementation p2p application with callback
2. Implementation p2p application by extending p2pnet.Node
3. Implementation of p2p security application

# Example 1 and 2
The examples 1 and 2 can be found in the documentation README.md in de main code. So, feel free to visit this specific file.

# Example 3: SecurityNode
This example (principally a real project to me) is about a decentralized peer-to-peer network application that creates security to its used. It provides different kind of security aspect to protect the data of the users. All nodes have a private/public key and signs all the messages they send. These messages are also verified. When successfull the application gets the message to process it. The messages are checked on integrity and non-repudiation.

## Python requirements
Use Python version 3.x and install the following modules:
1. pycryptodome

