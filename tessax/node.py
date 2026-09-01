from __future__ import annotations

from typing import List
from dataclasses import dataclass, field
import numpy as np

@dataclass
class Node():
    
    content: List[str] | None
    tag : List | None = None
    
    vector: List | None = None
    
    parent : Node | None = None
    title: str | None  = None
    
    children : List[Node]  = field(default_factory=list)
    
    
    def remove_node(self):
        
        self.parent.children.remove(self)
        
    
    def add_children(self, node : Node):
        self.children.append(node)
        
    def add_parent(self,children_nodes:List[Node]):
        
        for node in children_nodes:
            node.parent = self
              
        
    def add_sibling(self, text : str):
        
        sibling = Node(content=text, vector= self.vector, parent=self.parent,title=self.title,tag=self.tag,children=self.children)
        for orphan in sibling.children:
            orphan.parent = sibling
        if self.parent:
            self.parent.add_children(sibling)
        
    #Helper function to get all nodes from a node tree.
    def get_nodes(self):
        
        yield self
        
        for child in self.children[::-1]:
            
            yield from child.get_nodes()
            
    def merge_nodes(nodes:List[Node],merged_text):
        
        
        tags =  [tag for node in nodes for tag in node.tag]
        children = [child for node in nodes for child in node.children]
        

        mean_vector = None
        if nodes[0].vector is not None:
            vectors = [node.vector for node in nodes if node.vector is not None]
            stacked_vector = np.stack(vectors)
            mean_vector = np.mean(stacked_vector,axis=0)
        parent = nodes[0].parent
        new_node = Node(content=merged_text, parent=parent,title=nodes[0].title,tag=tags,children=children,vector=mean_vector)
        parent.add_children(new_node)
        new_node.add_parent(children)
    
   
        
            
        
                
                