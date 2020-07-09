import unittest
import time
import struct

from p2pnetwork.node import Node

"""
Author: Maurice Snoeren
Version: 0.1 beta (use at your own risk)

Testing the node communication by sending large amount of str and dict data
to see whether the node is correctly handling this.
TODO: testing sending bytes
TODO: bufferoverlow testing
"""
class TestNode(unittest.TestCase):
    """Testing the NodeConnection class."""

    def test_node_send_data_str(self):
        """Testing whether NodeConnections handle sending str well enough."""
        global messages
        messages = []

        class MyTestNode (Node):
            def __init__(self, host, port):
                super(MyTestNode, self).__init__(host, port, None)
                global messages
                messages.append("mytestnode started")
               
            def node_message(self, node, data):
                global messages
                messages.append(type(data))
                messages.append(len(data))
                
        node1 = MyTestNode("127.0.0.1", 10001)
        node2 = MyTestNode("127.0.0.1", 10002)
        node3 = MyTestNode("127.0.0.1", 10003)

        node1.start()
        node2.start()
        node3.start()

        node1.connect_with_node('127.0.0.1', 10002)
        time.sleep(2)

        node3.connect_with_node('127.0.0.1', 10001)
        time.sleep(2)

        # Create large message; large than used buffer 4096!
        data = ""
        for i in range(5000):
            data += "a"

        # Send multiple messages after each other (5 * 5000 bytes)
        node1.send_to_nodes(data)
        node1.send_to_nodes(data)
        node1.send_to_nodes(data)
        node1.send_to_nodes(data)
        node1.send_to_nodes(data)
        time.sleep(7)

        node1.stop()
        node2.stop()
        node3.stop()
        node1.join()
        node2.join()
        node3.join()

        self.assertTrue(len(messages) > 0, "There should have been sent some messages around!")
        self.assertEqual(len(messages), 23, "There should have been sent 23 message around!")
        
        self.assertEqual(messages[0],  "mytestnode started", "MyTestNode should have seen this event!")
        self.assertEqual(messages[1],  "mytestnode started", "MyTestNode should have seen this event!")
        self.assertEqual(messages[2],  "mytestnode started", "MyTestNode should have seen this event!")

        # Check if all the message are correctly received
        for i in range(0, 10, 2):
            self.assertEqual(str(messages[3+i]),  "<class 'str'>")
            self.assertEqual(messages[4+i],  5000)

    def test_node_send_data_dict(self):
        """Testing whether NodeConnections handle sending dict well enough."""
        global messages
        messages = []

        class MyTestNode (Node):
            def __init__(self, host, port):
                super(MyTestNode, self).__init__(host, port, None)
                global messages
                messages.append("mytestnode started")
               
            def node_message(self, node, data):
                global messages
                messages.append(type(data))
                messages.append(len(data["values"]))
                # messages.append("instance byte:" + isinstance(data, bytes))
                # Check the message here wether it is correct!
                
        node1 = MyTestNode("127.0.0.1", 10001)
        node2 = MyTestNode("127.0.0.1", 10002)
        node3 = MyTestNode("127.0.0.1", 10003)

        node1.start()
        node2.start()
        node3.start()

        node1.connect_with_node('127.0.0.1', 10002)
        time.sleep(2)

        node3.connect_with_node('127.0.0.1', 10001)
        time.sleep(2)

        # Create large message; large than used buffer 4096!
        data = { "type": "My Dict",
                 "values": []
        }
        for i in range(5000):
            data["values"].append("i: " + str(i))

        # Send multiple messages after each other (5 * 5000 bytes)
        node1.send_to_nodes(data)
        node1.send_to_nodes(data)
        node1.send_to_nodes(data)
        node1.send_to_nodes(data)
        node1.send_to_nodes(data)
        time.sleep(7)

        node1.stop()
        node2.stop()
        node3.stop()
        node1.join()
        node2.join()
        node3.join()

        self.assertTrue(len(messages) > 0, "There should have been sent some messages around!")
        self.assertEqual(len(messages), 23, "There should have been sent 23 message around!")
        
        self.assertEqual(messages[0],  "mytestnode started", "MyTestNode should have seen this event!")
        self.assertEqual(messages[1],  "mytestnode started", "MyTestNode should have seen this event!")
        self.assertEqual(messages[2],  "mytestnode started", "MyTestNode should have seen this event!")

        # Check if all the message are correctly received
        for i in range(0, 10, 2):
            self.assertEqual(str(messages[3+i]),  "<class 'dict'>")
            self.assertEqual(messages[4+i],  5000)
