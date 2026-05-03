from __future__ import annotations

from typing import List
from dataclasses import dataclass, field


@dataclass
class Node():
    tag : List 
    content: List[str] | None
    vector: List = None
    
    parent : Node | None = None
    title: str | None  = None
    
    children : List[Node] = field(default_factory=list)
    
    
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
        
        
    def __add__(self, other : Node):
        if ["h1","h2","h3"] in self.tag:
            return
        self.content = f"{self.content} {other.content} "

        for children in other.children:
            self.add_children(children)
        index = other.parent.children.index(other)
        del other.parent.children[index]
        for orphan in other.children:
            orphan.parent = self
    
    #Helper function to get all nodes from a node tree.
    def get_nodes(self):
        
        yield self
        
        for child in self.children:
            
            yield from child.get_nodes()
            
    def merge_nodes(nodes:List[Node],merged_text):
        
        
        tags =  [tag for node in nodes for tag in node.tag]
        children = [child for node in nodes for child in node.children]
        
        parent = nodes[0].parent
        new_node = Node(content=merged_text, parent=parent,title=nodes[0].title,tag=tags,children=children)
        parent.add_children(new_node)
        new_node.add_parent(children)
    
   
        
            
        
                
                