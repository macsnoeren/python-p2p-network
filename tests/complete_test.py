from p2pnet import Node
import time


def node_callback(event, node, connected_node, data):
    if event == 'node_message':
        print('message from {}:{} to {}:{}'.format(connected_node.host, connected_node.port, node.host, node.port))
        print(data['data'])
        if 'op' in data.keys():
            if data['op'] == 'propagation':
                node.send_to_nodes(data, exclude=[connected_node])
    else:
        print('{} in node <{}:{}>'.format(event, node.host, node.port))


node_0 = Node('127.0.0.1', 8000, node_callback)
node_1 = Node('127.0.0.1', 8001, node_callback)
node_2 = Node('127.0.0.1', 8002, node_callback)

if __name__ == '__main__':
    node_0.start()
    node_1.start()
    node_2.start()

    time.sleep(1)
    print('Test connections')
    print('node 0 -> node 1')
    node_0.connect_with_node('127.0.0.1', 8001)
    time.sleep(2)

    print('node 2 -> node 0')
    node_2.connect_with_node('127.0.0.1', 8000)
    time.sleep(2)

    print('show node 0 connections:')
    for connection in node_0.all_nodes:
        print(connection)

    time.sleep(2)
    print('Send Message Test:')
    print('Node 0 -> All')
    node_0.send_to_nodes({'data': 'hello everyone'})

    time.sleep(2)
    print('propagate a message node 2 -> (all) node 0 -> node 1')
    node_2.send_to_nodes({'data': 'hello sender are node 2', 'op': 'propagation'})

    node_0.stop()
    node_1.stop()
    node_2.stop()
    print('end test')
