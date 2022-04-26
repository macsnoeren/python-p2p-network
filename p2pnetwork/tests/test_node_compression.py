import unittest
import time

from p2pnetwork.node import Node

"""
Author: Maurice Snoeren
Version: 0.1 beta (use at your own risk)

Testing the compression functionality that has been added.
"""

class TestNode(unittest.TestCase):
    """Testing communication compression of the Node class."""

    def test_node_compression_zlib(self):
        """Testing the zlib compression."""
        global message
        message = []

        # Using the callback we are able to see the events and messages of the Node
        def node_callback(event, main_node, connected_node, data):
            global message
            try:
                if event == "node_message":
                    message.append(event + ":" + main_node.id + ":" + connected_node.id + ":" + str(data))

            except Exception as e:
                message = "exception: " + str(e) 

        node1 = Node(host="localhost", port=10001, callback=node_callback)
        node2 = Node(host="localhost", port=10002, callback=node_callback)

        node1.start()
        node2.start()
        time.sleep(2)

        node1.connect_with_node("localhost", 10002)
        time.sleep(2)

        node1.send_to_nodes("Hi from node 1!", compression='zlib')
        time.sleep(1)
        node1_message = message

        node2.send_to_nodes("Hi from node 2!", compression='zlib')
        time.sleep(1)
        node2_message = message

        node1.stop()
        node2.stop()
        node1.join()
        node2.join()

        time.sleep(10)
        
        self.assertIn("Hi from node", message[0], "The message is not correctly received")
        self.assertIn("Hi from node", message[1], "The message is not correctly received")

    def test_node_compression_lzma(self):
        """Testing the lzma compression."""
        global message
        message = []

        # Using the callback we are able to see the events and messages of the Node
        def node_callback(event, main_node, connected_node, data):
            global message
            try:
                if event == "node_message":
                    message.append(event + ":" + main_node.id + ":" + connected_node.id + ":" + str(data))

            except Exception as e:
                message = "exception: " + str(e) 

        node1 = Node(host="localhost", port=10001, callback=node_callback)
        node2 = Node(host="localhost", port=10002, callback=node_callback)

        node1.start()
        node2.start()
        time.sleep(2)

        node1.connect_with_node("localhost", 10002)
        time.sleep(2)

        node1.send_to_nodes("Hi from node 1!", compression='lzma')
        time.sleep(1)
        node1_message = message

        node2.send_to_nodes("Hi from node 2!", compression='lzma')
        time.sleep(1)
        node2_message = message

        node1.stop()
        node2.stop()
        node1.join()
        node2.join()

        time.sleep(10)
        
        self.assertIn("Hi from node", message[0], "The message is not correctly received")
        self.assertIn("Hi from node", message[1], "The message is not correctly received")

    def test_node_compression_bzip2(self):
        """Testing the bzip2 compression."""
        global message
        message = []

        # Using the callback we are able to see the events and messages of the Node
        def node_callback(event, main_node, connected_node, data):
            global message
            try:
                if event == "node_message":
                    message.append(event + ":" + main_node.id + ":" + connected_node.id + ":" + str(data))

            except Exception as e:
                message = "exception: " + str(e) 

        node1 = Node(host="localhost", port=10001, callback=node_callback)
        node2 = Node(host="localhost", port=10002, callback=node_callback)

        node1.start()
        node2.start()
        time.sleep(2)

        node1.connect_with_node("localhost", 10002)
        time.sleep(2)

        node1.send_to_nodes("Hi from node 1!", compression='bzip2')
        time.sleep(1)
        node1_message = message

        node2.send_to_nodes("Hi from node 2!", compression='bzip2')
        time.sleep(1)
        node2_message = message

        node1.stop()
        node2.stop()
        node1.join()
        node2.join()

        time.sleep(10)
        
        self.assertIn("Hi from node", message[0], "The message is not correctly received")
        self.assertIn("Hi from node", message[1], "The message is not correctly received")

    def test_node_compression_unknown(self):
        """Testing when the compression is unknown."""
        global message
        message = []

        # Using the callback we are able to see the events and messages of the Node
        def node_callback(event, main_node, connected_node, data):
            global message
            try:
                if event == "node_message":
                    message.append(event + ":" + main_node.id + ":" + connected_node.id + ":" + str(data))

            except Exception as e:
                message = "exception: " + str(e) 

        node1 = Node(host="localhost", port=10001, callback=node_callback)
        node2 = Node(host="localhost", port=10002, callback=node_callback)

        node1.start()
        node2.start()
        time.sleep(2)

        node1.connect_with_node("localhost", 10002)
        time.sleep(2)

        node1.send_to_nodes("Hi from node 1!", compression='unknown')
        time.sleep(1)
        node1_message = message

        node2.send_to_nodes("Hi from node 2!", compression='unknown')
        time.sleep(1)
        node2_message = message

        node1.stop()
        node2.stop()
        node1.join()
        node2.join()

        time.sleep(10)
        
        self.assertEqual(len(message), 0, "No messages should have been send")

if __name__ == '__main__':
    unittest.main()
