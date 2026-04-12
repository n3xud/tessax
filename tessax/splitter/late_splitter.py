from tessax.splitter import HTMLSplitter
from tessax.node import Node
import tessax.tools

class LateSplitter(HTMLSplitter):
    
    
    
    
    def split_combine(self,root_node:Node):
        
        undersized_node = None
        for node in list(root_node.children):
           
            if self.split_combine(node):
                if undersized_node:
                    undersized_node + node
                else:    
                    undersized_node = node
            else:
                
                node._split(chunk_size=self.config.chunk_size)
                 
        return (tools.get_token_length(root_node.content)<=self.config.chunk_size)