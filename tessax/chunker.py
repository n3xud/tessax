from abc import ABC, abstractmethod
from tessax.node import Node
import tessax.embedding as model
from tessax.node import Node

import tessax.embedding as model

class Chunker(ABC):


    def process_vectorization(self,root_node:Node):
        self.vectorize(root_node)
       


    def vectorize(self,root_node:Node) -> Node:
        for node in root_node.get_nodes():
            if node.content:
                embedding = model.create_doc_embedding(" ".join(node.content))
                node.vector = embedding
        
        return root_node
    