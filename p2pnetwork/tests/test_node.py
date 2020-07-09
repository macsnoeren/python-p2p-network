import unittest
import time

from p2pnetwork.node import Node

"""
Author: Maurice Snoeren
Version: 0.1 beta (use at your own risk)

Testing the node on its basic functionality, like connecting to other nodes and
sending data around. Furthermore, the events are tested whether they are handled
correctly in the case of the callback and in the case of extending the class.
"""

class TestNode(unittest.TestCase):
    """Testing the Node class."""

    def test_node_connection(self):
        """Testing whether two Node instances are able to connect with each other."""
        node1 = Node("localhost", 10001)
        node2 = Node("localhost", 10002)

        node1.start()
        node2.start()
        time.sleep(2)

        step_1_node1_total_inbound_nodes = len(node1.nodes_inbound)
        step_1_node1_total_outbound_nodes = len(node1.nodes_outbound)
        step_1_node2_total_inbound_nodes = len(node2.nodes_inbound)
        step_1_node2_total_outbound_nodes = len(node2.nodes_outbound)

        node1.connect_with_node("localhost", 10001)
        time.sleep(1)

        step_2_node1_total_inbound_nodes = len(node1.nodes_inbound)
        step_2_node1_total_outbound_nodes = len(node1.nodes_outbound)

        node1.connect_with_node("localhost", 10002)
        time.sleep(2)

        step_3_node1_total_inbound_nodes = len(node1.nodes_inbound)
        step_3_node1_total_outbound_nodes = len(node1.nodes_outbound)
        step_3_node2_total_inbound_nodes = len(node2.nodes_inbound)
        step_3_node2_total_outbound_nodes = len(node2.nodes_outbound)

        node1.stop()
        node2.stop()
        node1.join()
        node2.join()

        self.assertEqual(step_1_node1_total_inbound_nodes, 0, "The node 1 should not have any inbound nodes.")
        self.assertEqual(step_1_node1_total_outbound_nodes, 0, "The node 1 should not have any outbound nodes.")
        self.assertEqual(step_1_node2_total_inbound_nodes, 0, "The node 2 should not have any inbound nodes.")
        self.assertEqual(step_1_node2_total_outbound_nodes, 0, "The node 2 should not have any outbound nodes.")

        self.assertEqual(step_2_node1_total_inbound_nodes, 0, "The node 1 should not have any inbound nodes.")
        self.assertEqual(step_2_node1_total_outbound_nodes, 0, "The node 1 should not have any outbound nodes.")

        self.assertEqual(step_3_node1_total_inbound_nodes, 0, "The node 1 should not have any inbound node.")
        self.assertEqual(step_3_node1_total_outbound_nodes, 1, "The node 1 should have one outbound nodes.")
        self.assertEqual(step_3_node2_total_inbound_nodes, 1, "The node 2 should have one inbound node.")
        self.assertEqual(step_3_node2_total_outbound_nodes, 0, "The node 2 should not have any outbound nodes.")

    def test_node_communication(self):
        """Test whether the connected nodes are able to send messages to each other."""
        global message
        message = "unknown"

        # Using the callback we are able to see the events and messages of the Node
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

        time.sleep(10)
        
        self.assertEqual("node_message:" + node2.id + ":" + node1.id + ":Hi from node 1!", node1_message, "The message is not correctly received by node 2")
        self.assertEqual("node_message:" + node1.id + ":" + node2.id + ":Hi from node 2!", node2_message, "The message is not correctly received by node 1")

    def test_node_complete(self):
        """Testing the complete sequence of the Node based on Samuel complete_test.py."""

        global message
        message = []

        # Using the callback we are able to see the events and messages of the Node
        def node_callback(event, main_node, connected_node, data):
            global message
            try:
                if event == "node_message":
                    message.append(event + ":" + main_node.id + ":" + connected_node.id + ":" + str(data))

            except Exception as e:
                message.append("exception: " + str(e))

        node_0 = Node('127.0.0.1', 10000, node_callback)
        node_1 = Node('127.0.0.1', 10001, node_callback)
        node_2 = Node('127.0.0.1', 10002, node_callback)

        node_0.start()
        node_1.start()
        node_2.start()
        time.sleep(1)

        # Test the connections
        node_0.connect_with_node('127.0.0.1', 10001)
        time.sleep(2)

        node_0_connections = node_0.nodes_outbound
        step_1_node_0_total_connections = len(node_0_connections) # should be 1
        step_1_node_0_connection_node = "none"
        if step_1_node_0_total_connections > 0:
            step_1_node_0_connection_node = node_0_connections[0].id + ":" + node_0_connections[0].host + ":" + str(node_0_connections[0].port) # node1.id:127.0.0.1:10001

        node_1_connections = node_1.nodes_inbound
        step_1_node_1_total_connections = len(node_1_connections)
        step_1_node_1_connection_node = "none"
        if step_1_node_1_total_connections > 0:
            step_1_node_1_connection_node = node_1_connections[0].id + ":" + node_1_connections[0].host # node0.id:127.0.0.1, inbound port is port of client

        node_2.connect_with_node('127.0.0.1', 10000)
        time.sleep(2)

        node_2_connections = node_2.nodes_outbound
        step_2_node_2_total_connections = len(node_2_connections) # should be 1
        step_2_node_2_connection_node = "none"
        if step_2_node_2_total_connections > 0:
            step_2_node_2_connection_node = node_2_connections[0].id + ":" + node_2_connections[0].host + ":" + str(node_2_connections[0].port) # node0.id:127.0.0.1:10000

        node_0_connections = node_0.nodes_inbound
        step_2_node_0_total_connections = len(node_2_connections) # should be 1
        step_2_node_0_connection_node = "none"
        if step_2_node_0_total_connections > 0:
            step_2_node_0_connection_node = node_0_connections[0].id + ":" + node_0_connections[0].host # node2.id:127.0.0.1

        # Send messages
        node_0.send_to_nodes('hello from node 0')
        time.sleep(2)

        node_1.send_to_nodes('hello from node 1')
        time.sleep(2)

        node_2.send_to_nodes('hello from node 2')
        time.sleep(2)

        node_0.stop()
        node_1.stop()
        node_2.stop()
        node_0.join()
        node_1.join()
        node_2.join()
       
        # Perform the asserts!
        self.assertEqual(step_1_node_0_total_connections, 1, "Node 0 should have one outbound connection.")
        self.assertEqual(step_1_node_0_connection_node, node_1.id + ":127.0.0.1:10001", "Node 0 should be connected (outbound) with node 1.")
        self.assertEqual(step_1_node_1_total_connections, 1, "Node 1 should have one inbound connection.")
        self.assertEqual(step_1_node_1_connection_node, node_0.id + ":127.0.0.1", "Node 1 should be connected (inbound) with node 0.")

        self.assertEqual(step_2_node_2_total_connections, 1, "Node 2 shoud have one outbound connection.")
        self.assertEqual(step_2_node_2_connection_node, node_0.id + ":127.0.0.1:10000", "Node 2 should be connected (outbound) with node 0.")
        self.assertEqual(step_2_node_0_total_connections, 1, "Node 0 should have one inbound connection.")
        self.assertEqual(step_2_node_0_connection_node, node_2.id + ":127.0.0.1", "Node 0 should be connected (inbound) with node 2.")

        self.assertTrue(len(message) > 0, "There should have been sent some messages around!")
        self.assertTrue(len(message) == 4, "There should have been sent 4 message around!")
        self.assertEqual(message[0], "node_message:" + node_2.id + ":" + node_0.id + ":hello from node 0", "Node 2 should have received a message from node 0")
        self.assertEqual(message[1], "node_message:" + node_1.id + ":" + node_0.id + ":hello from node 0", "Node 1 should have received a message from node 0")
        self.assertEqual(message[2], "node_message:" + node_0.id + ":" + node_1.id + ":hello from node 1", "Node 0 should have received a message from node 1")
        self.assertEqual(message[3], "node_message:" + node_0.id + ":" + node_2.id + ":hello from node 2", "Node 0 should have received a message from node 2")

    def test_node_events(self):
        """Testing the events that are triggered by the Node."""

        global message
        message = []

        # Using the callback we are able to see the events and messages of the Node
        def node_callback(event, main_node, connected_node, data):
            global message
            message.append(event + ":" + main_node.id)                

        node_0 = Node('127.0.0.1', 10000, node_callback)
        node_1 = Node('127.0.0.1', 10001, node_callback)
        node_2 = Node('127.0.0.1', 10002, node_callback)

        node_0.start()
        node_1.start()
        node_2.start()
        time.sleep(1)

        # Test the connections
        node_0.connect_with_node('127.0.0.1', 10001)
        time.sleep(2)

        node_2.connect_with_node('127.0.0.1', 10000)
        time.sleep(2)

        # Send messages
        node_0.send_to_nodes('hello from node 0')
        time.sleep(2)

        node_1.send_to_nodes('hello from node 1')
        time.sleep(2)

        node_2.send_to_nodes('hello from node 2')
        time.sleep(2)

        node_0.stop()
        node_1.stop()
        node_2.stop()
        node_0.join()
        node_1.join()
        node_2.join()

        print(str(message))

        # Perform the asserts!
        self.assertTrue(len(message) > 0, "There should have been sent some messages around!")
        self.assertTrue(len(message) == 11, "There should have been sent 4 message around!")

        if "outbound" in message[0]:
            self.assertEqual(message[0],  "outbound_node_connected:" + node_0.id, "Event should have occurred")
            self.assertEqual(message[1],  "inbound_node_connected:" + node_1.id, "Event should have occurred")
        else:
            self.assertEqual(message[1],  "outbound_node_connected:" + node_0.id, "Event should have occurred")
            self.assertEqual(message[0],  "inbound_node_connected:" + node_1.id, "Event should have occurred")
        
        if "outbound" in message[2]:
            self.assertEqual(message[2],  "outbound_node_connected:" + node_2.id, "Event should have occurred")
            self.assertEqual(message[3],  "inbound_node_connected:" + node_0.id, "Event should have occurred")
        else:
            self.assertEqual(message[3],  "outbound_node_connected:" + node_2.id, "Event should have occurred")
            self.assertEqual(message[2],  "inbound_node_connected:" + node_0.id, "Event should have occurred")

        if  node_2.id in message[4]:
            self.assertEqual(message[4],  "node_message:" + node_2.id, "Event should have occurred")
            self.assertEqual(message[5],  "node_message:" + node_1.id, "Event should have occurred")
        else:
            self.assertEqual(message[5],  "node_message:" + node_2.id, "Event should have occurred")
            self.assertEqual(message[4],  "node_message:" + node_1.id, "Event should have occurred")

        self.assertEqual(message[6],  "node_message:" + node_0.id, "Event should have occurred")
        self.assertEqual(message[7],  "node_message:" + node_0.id, "Event should have occurred")
        self.assertEqual(message[8],  "node_request_to_stop:" + node_0.id, "Event should have occurred")
        self.assertEqual(message[9],  "node_request_to_stop:" + node_1.id, "Event should have occurred")
        self.assertEqual(message[10], "node_request_to_stop:" + node_2.id, "Event should have occurred")

    def test_extending_class_of_node(self):
        """Testing the class implementation of the Node."""

        global message
        message = []

        class MyTestNode (Node):
            def __init__(self, host, port):
                super(MyTestNode, self).__init__(host, port, None)
                global message
                message.append("mytestnode started")

            def outbound_node_connected(self, node):
                global message
                message.append("outbound_node_connected: " + node.id)
                
            def inbound_node_connected(self, node):
                global message
                message.append("inbound_node_connected: " + node.id)

            def inbound_node_disconnected(self, node):
                global message
                message.append("inbound_node_disconnected: " + node.id)

            def outbound_node_disconnected(self, node):
                global message
                message.append("outbound_node_disconnected: " + node.id)

            def node_message(self, node, data):
                global message
                message.append("node_message from " + node.id + ": " + str(data))
                
            def node_disconnect_with_outbound_node(self, node):
                global message
                message.append("node wants to disconnect with oher outbound node: " + node.id)
                
            def node_request_to_stop(self):
                global message
                message.append("node is requested to stop!")

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

        # Send messages
        node1.send_to_nodes('hello from node 1')
        time.sleep(2)

        node2.send_to_nodes('hello from node 2')
        time.sleep(2)

        node3.send_to_nodes('hello from node 3')
        time.sleep(2)

        node1.stop()
        node2.stop()
        node3.stop()
        node1.join()
        node2.join()
        node3.join()

        self.assertTrue(len(message) > 0, "There should have been sent some messages around!")
        self.assertTrue(len(message) == 14, "There should have been sent 14 message around!")

        self.assertEqual(message[0],  "mytestnode started", "MyTestNode should have seen this event!")
        self.assertEqual(message[1],  "mytestnode started", "MyTestNode should have seen this event!")
        self.assertEqual(message[2],  "mytestnode started", "MyTestNode should have seen this event!")

        if "inbound" in message[3]:
            self.assertEqual(message[3],  "inbound_node_connected: " + node1.id, "MyTestNode should have seen this event!")
            self.assertEqual(message[4],  "outbound_node_connected: " + node2.id, "MyTestNode should have seen this event!")
        else:
            self.assertEqual(message[4],  "inbound_node_connected: " + node1.id, "MyTestNode should have seen this event!")
            self.assertEqual(message[3],  "outbound_node_connected: " + node2.id, "MyTestNode should have seen this event!")

        if "outbound" in message[5]:
            self.assertEqual(message[5],  "outbound_node_connected: " + node1.id, "MyTestNode should have seen this event!")
            self.assertEqual(message[6],  "inbound_node_connected: " + node3.id, "MyTestNode should have seen this event!")
        else:
            self.assertEqual(message[6],  "outbound_node_connected: " + node1.id, "MyTestNode should have seen this event!")
            self.assertEqual(message[5],  "inbound_node_connected: " + node3.id, "MyTestNode should have seen this event!")

        self.assertEqual(message[7],  "node_message from " + node1.id + ": hello from node 1", "MyTestNode should have seen this event!")
        self.assertEqual(message[8],  "node_message from " + node1.id + ": hello from node 1", "MyTestNode should have seen this event!")
        self.assertEqual(message[9],  "node_message from " + node2.id + ": hello from node 2", "MyTestNode should have seen this event!")
        self.assertEqual(message[10],  "node_message from " + node3.id + ": hello from node 3", "MyTestNode should have seen this event!")

        self.assertEqual(message[11],  "node is requested to stop!", "MyTestNode should have seen this event!")
        self.assertEqual(message[12],  "node is requested to stop!", "MyTestNode should have seen this event!")
        self.assertEqual(message[13],  "node is requested to stop!", "MyTestNode should have seen this event!")

if __name__ == '__main__':
    unittest.main()
