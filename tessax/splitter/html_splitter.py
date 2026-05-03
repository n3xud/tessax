from abc import ABC, abstractmethod
import typing as t
from queue import Queue

from tessax.node import Node
from tessax.embedding import get_token_length
from tessax.config import RAGConfig

class HTMLSplitter(ABC):
    
    def __init__(self,config:RAGConfig):
        self.config = config
    
    @abstractmethod
    def merge(self,root_node:Node):
        
        q = Queue()
        q.put(root_node)
        
        while not q.empty():
            nodes = []
            node : Node = q.get()
        
        #Puts every  child node in a node list
            for child in node.children:
                q.put(child)
                if child.content:
                    nodes.append(child)

            if nodes:
                #merged text
                tmp_merged=[]
                #counter for getting nodes to merge
                set_index = 0 
                prev_text = None
                for index ,node in enumerate(nodes):
                    
                    for text in node.content:
                        if prev_text:         
                            tokens1 = get_token_length(prev_text)
                        
                            tokens2 = get_token_length(text)
                        
                            if tokens1 + tokens2 < self.config.chunk_size:
                            
                                tmp_merged.append(text)
                                
                            else:
                            
                                if set_index==index:
                            
                                    Node.merge_nodes([nodes[set_index]],tmp_merged)
                                else:
                                    Node.merge_nodes(nodes[set_index:index],tmp_merged)
                                
                                tmp_merged = [text]
                                set_index = index
                        else:
                            tmp_merged = [text]
                        prev_text = text
                        
                if set_index==len(nodes) - 1:
                
                    Node.merge_nodes([nodes[set_index]],tmp_merged)
                else:
                    Node.merge_nodes(nodes[set_index:],tmp_merged)  
                
                
                
                for node in nodes:
                    node.remove_node()
    @abstractmethod
    def vectorize():
        pass
    