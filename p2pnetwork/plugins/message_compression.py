import zlib, bz2, lzma, base64

from p2pnetwork.plugin import NodePlugin

class PluginMessageCompression(NodePlugin):
    """This plugin implements compression on the message that is send between the nodes."""
       
    def __init__(self, compression='zlib'):
        """Create instance of PluginMessageCompression."""
        super().__init__()

        self._compression = compression

    def node_send_data(self, data, encoding_type):
        """When the node is sending data, this method is called. The plugin is able to add a protocol
           or to add compression."""
        data = self.compress(data, self._compression)

        return (True, data)

    def node_received_message(self, node, data) -> bool:
        """This method is called when the node received data from another node. The plugin is able to check
           whether this method is required to be processed. When the plugin decides that the data is going
           to be processed, it returns True otherwise False."""
        return False

    def compress(self, data, compression):
        """Compresses the data given the type. It is used to provide compression to lower the network traffic in case of
           large data chunks. It stores the compression type inside the data, so it can be easily retrieved."""

        self.main_node.debug_print(self.id + ":compress:" + compression)
        self.main_node.debug_print(self.id + ":compress:input: " + str(data))

        compressed = data

        try:
            if self._compression == 'zlib':
                compressed = base64.b64encode( zlib.compress(data, 6) + b'zlib' )
            
            elif self._compression == 'bzip2':
                compressed = base64.b64encode( bz2.compress(data) + b'bzip2' )
            
            elif self._compression == 'lzma':
                compressed = base64.b64encode( lzma.compress(data) + b'lzma' )

            else:
                self.main_node.debug_print(self.id + ":compress:Unknown compression")
                return None

        except Exception as e:
            self.main_node.debug_print("compress: exception: " + str(e))

        self.main_node.debug_print(self.id + ":compress:b64encode:" + str(compressed))
        self.main_node.debug_print(self.id + ":compress:compression:" + str(int(10000*len(compressed)/len(data))/100) + "%")

        return compressed

    def decompress(self, compressed):
        """Decompresses the data given the type. It is used to provide compression to lower the network traffic in case of
           large data chunks."""
        self.main_node.debug_print(self.id + ":decompress:input: " + str(compressed))
        compressed = base64.b64decode(compressed)
        self.main_node.debug_print(self.id + ":decompress:b64decode: " + str(compressed))

        try:
            if compressed[-4:] == b'zlib':
                compressed = zlib.decompress(compressed[0:len(compressed)-4])
            
            elif compressed[-5:] == b'bzip2':
                compressed = bz2.decompress(compressed[0:len(compressed)-5])
            
            elif compressed[-4:] == b'lzma':
                compressed = lzma.decompress(compressed[0:len(compressed)-4])

        except Exception as e:
            print("Exception: " + str(e))

        self.main_node.debug_print(self.id + ":decompress:result: " + str(compressed))

        return compressed

    def __str__(self):
        return str(self.__class__.__name__)

    def __repr__(self):
        return str(self.__class__)
