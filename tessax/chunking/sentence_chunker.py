
from typing import Optional
from bs4 import Tag
import copy


class SentenceChunking(BaseChunking):
    """Sentence chunking."""
    
    def __init__(self):
        super().__init__()
  
    def extract_html(self, element,content_list,url): 
        for child in element.children:
            if isinstance(child,Tag):
                  
                    
                    child_cont = child.find_all(string=True,recursive=False)
                    if child_cont:
    
                        

                        sentences = self.llama_sentence_splitter.split_text(child_cont[0])
                        for sentence in sentences:
                            
                            if len(sentence)>1:
                                content_list.append({"type":"txt","content": sentence,"src":url})
                                
                            
                self.extract_html(child, content_list,url)
        return content_list
    
    @staticmethod
    def add_window(content_list,range):
        tmp_list = copy.deepcopy(content_list) #slow
        for index, node in enumerate(content_list):
            start = max(index - range, 0)
            end = min(index + range+1, len(content_list))
            list_range= tmp_list[start:end]
            node["window"] = list_range

    @staticmethod
    def filter(content_list,images):
        if images:
            pass
        else:
            content_list = filter(lambda x: x["type"] == "txt", content_list)
            
        return list(content_list)
    