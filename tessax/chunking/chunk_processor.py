from enum import Enum
from typing import Dict, List, Optional, Tuple, cast







    """
        Handles base chunking processes for different chunking methods.
    """
  
    def chunk(
              soup,
              url,
              mode: Optional[CHUNK_MODES] = CHUNK_MODES.BASE_CHUNKING
        ) -> None:
        soup = self.base_chunking.setup_html(soup)
        
        if mode == CHUNK_MODES.SENTENCE_CHUNKING:
            titel = self.azure_openai.generate_titel(soup.get_text()) 

            content_list = self.sentence_chunking.extract_html(soup,[],url)
            
            content_list = self.sentence_chunking.filter(content_list,False)
            
            self.sentence_chunking.add_window(content_list,10)
            for node in content_list:
                self.sentence_chunking.pushToVector(node['content'],node["src"],node['type'],node["window"])
        elif mode == CHUNK_MODES.SEMANTIC_CHUNKING:
            if config.TITEL == "True":
                titel = self.azure_openai.generate_titel(soup.get_text()) 
                print("titel generated")
                print(titel)

            else:
                titel = ""
            content_list = self.semantic_chunking.extract_html(soup,[],url)
            print("html extracted")
            content_list = self.semantic_chunking.filter(content_list,False)
            print("filtered")
            content_list = self.semantic_chunking.base(content_list)
            print("semantic process finished")
            self.semantic_chunking.add_window(content_list,3)
            print("added window")
        
            for node in content_list:
                self.semantic_chunking.pushToVector(titel + " "+node['content'],node["src"],node['type'],node["window"],"")
                

        elif mode == CHUNK_MODES.CONTEXTUAL_CHUNKING:
            content_list = self.semantic_chunking.extract_html(soup,[],url)
            content_list = self.semantic_chunking.filter(content_list,False)
            content_list = self.semantic_chunking.base(content_list)

            for node in content_list:
                contextual_text = self.azure_openai.contextual_generation(node['content'],soup.get_text())
                print(contextual_text+node['content'])
                self.semantic_chunking.pushToVector(contextual_text + node['content'],node["src"],node['type'],"","")

        elif mode == CHUNK_MODES.BASE_CHUNKING:
            
            self.base_chunking.extract_html(soup,url)
            
        
