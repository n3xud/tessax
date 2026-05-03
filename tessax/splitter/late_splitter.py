from tessax.splitter import HTMLSplitter
from tessax.node import Node
import tessax.tools
import tessax.embedding as model

import torch
class LateSplitter(HTMLSplitter):
    
    
    def merge(self,node):
        return super().merge(node)
    
    def vectorize(self,root_node:Node):
        
        sentences = []
        
        for node in root_node.get_nodes():
            if node.content:
                sentences.append(node.content)
        
            
      
        sentences_single = [sentences_single for stack in sentences for sentences_single in stack]
       
        string = "".join(sentences_single)
        
        hidden_states,offset_mapping = model._get_hidden_states(string)
        
        offset_mapping = offset_mapping.squeeze(0)  
        hidden_states = hidden_states.squeeze(0)   
        
            
        i = 0
        start = 0
        tmp_m = []
        for node in root_node.get_nodes():
            if node.content:
                len_c = len("".join(node.content))          
                while i + 1 < len(offset_mapping) and offset_mapping[i+1][1] <= start + len_c:        
                    tmp_m.append(hidden_states[i]) 
                    i += 1
                      
                tmp_m.append(hidden_states[i])    
                
                    
                i += 1
                
                if  i + 1 < len(offset_mapping) and offset_mapping[i][0] < start + len_c:
                    tmp_m.append(hidden_states[i])               
                start = start + len_c          
                
                #Mean pooling
                mean = torch.stack(tmp_m).mean(dim=0)
                node.vector = mean.cpu().float().numpy()
                
                tmp_m = []
                
        
       