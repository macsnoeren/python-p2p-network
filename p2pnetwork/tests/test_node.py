import unittest
import time

from p2pnetwork.node import Node

class TestNode(unittest.TestCase):
    """Testing the Node class."""

    def test_node_connection(self):
        """Testing whether two Node instances are able to connect with each other."""
        node1 = Node("localhost", 10001)
        node2 = Node("localhost", 10002)

        node1.start()
        node2.start()
        time.sleep(2)

        self.assertEqual(len(node1.nodes_inbound), 0, "The node 1 should not have any inbound nodes.")
        self.assertEqual(len(node1.nodes_outbound), 0, "The node 1 should not have any outbound nodes.")
        self.assertEqual(len(node2.nodes_inbound), 0, "The node 2 should not have any inbound nodes.")
        self.assertEqual(len(node2.nodes_outbound), 0, "The node 2 should not have any outbound nodes.")

        node1.connect_with_node("localhost", 10001)
        time.sleep(1)

        self.assertEqual(len(node1.nodes_inbound), 0, "The node 1 should not have any inbound nodes.")
        self.assertEqual(len(node1.nodes_outbound), 0, "The node 1 should not have any outbound nodes.")

        node1.connect_with_node("localhost", 10002)
        time.sleep(2)

        total_nodes_inbound_1 = len(node1.nodes_inbound)
        total_nodes_outbound_1= len(node1.nodes_outbound)
        total_nodes_inbound_2 = len(node2.nodes_inbound)
        total_nodes_outbound_2 = len(node2.nodes_outbound)

        node1.stop()
        node2.stop()
        node1.join()
        node2.join()

        self.assertEqual(total_nodes_inbound_1, 0, "The node 1 should not have any inbound node.")
        self.assertEqual(total_nodes_outbound_1, 1, "The node 1 should have one outbound nodes.")
        self.assertEqual(total_nodes_inbound_2, 1, "The node 2 should have one inbound node.")
        self.assertEqual(total_nodes_outbound_2, 0, "The node 2 should not have any outbound nodes.")

    def test_node_communication(self):
        """Test whether the connected nodes are able to send messages to each other."""
        global message
        message = "unknown"

        def node_callback(event, main_node, connected_node, data):
            global message
            try:
                if event == "node_message":
                    message = event + ":" + main_node.id + ":" + connected_node.id + ":" + str(data)

            except Exception as e:
                message = "exception: " + str(e) 

        node1 = Node("localhost", 10001, node_callback)
        node2 = Node("localhost", 10002, node_callback)

        node1.start()
        node2.start()
        time.sleep(2)

        node1.connect_with_node("localhost", 10002)
        time.sleep(2)

        node1.send_to_nodes("Hi from node 1!")
        time.sleep(1)
        node1_message = message

        node2.send_to_nodes("Hi from node 2!")
        time.sleep(1)
        node2_message = message

        node1.stop()
        node2.stop()
        node1.join()
        node2.join()

        self.maxDiff = None
        self.assertEqual("node_message:" + node2.id + ":" + node1.id + ":Hi from node 1!", node1_message, "The message is not correctly received by node 2")
        self.assertEqual("node_message:" + node1.id + ":" + node2.id + ":Hi from node 2!", node2_message, "The message is not correctly received by node 1")

# TODO: event check using the callback function?!
# TODO: class implementation check?!

if __name__ == '__main__':
    unittest.main()