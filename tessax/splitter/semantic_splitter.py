from tessax.splitter import HTMLSplitter
from bs4 import BeautifulSoup,Tag

from tessax.node import Node
from typing import List
from tessax.config import RAGConfig

import tessax.embedding as model

class SemanticSplitter(HTMLSplitter):
    
    
       
    def merge(self,root_node:Node):
        
        nodes: List[Node]=[]
        
        
        for node in root_node.children:
            if node.content:
                nodes.append(node)
                
            self.merge(node)
            
        #Extract all Sentences from sibling nodes into new list    
        sentences = [text for node in nodes for text in node.content]
        
        if sentences:
            
            tmp_merged = [sentences[0]]    
            
            set_index = 0
            prev_text = None
            for index ,node in enumerate(nodes):
                for text in node.content:
                    if prev_text:         
                        embedding1 = model.create_embedding(prev_text)
                        embedding2 = model.create_embedding(text)
                        similarity = model._get_similarities(embedding1,embedding2)
                        if similarity> self.config.simil:
                            
                            tmp_merged.append(text)
                            
                        else:
                            if set_index==index:
                        
                                Node.merge_nodes([nodes[index]],tmp_merged)
                            else:
                                Node.merge_nodes(nodes[set_index:index],tmp_merged)
                            
                            tmp_merged = [text]
                            set_index = index
                    prev_text = text
            if set_index==len(nodes)-1:
            
                Node.merge_nodes([nodes[set_index]],tmp_merged)
            else:
                Node.merge_nodes(nodes[set_index:len(nodes)-1],tmp_merged)  
            
            
            
            for node in nodes:
                node.remove_node()
                    
    def vectorize(self,root_node:Node):
        for node in root_node.get_nodes():
            if node.content:
                embedding = model.create_embedding(" ".join(node.content))
                node.vector = embedding