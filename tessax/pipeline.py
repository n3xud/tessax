
from .html_reader import HTMLReader
from .splitter import *
from .config import RAGConfig

#import tessax.qa
from pydantic import BaseModel,model_validator,ConfigDict
from typing import List
from tessax.node import Node
from . import database

from .splitter import SemanticSplitter
class RAGPipeline(BaseModel):
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    pages : List[str]
    config : RAGConfig 
  
    #index : Index
    htmlsplitter : HTMLSplitter = None
    htmlreader : HTMLReader = None
    #evaluation : Evaluation
    
    
    
    @model_validator(mode="after")
    def initialize_components(self) -> "RAGPipeline":

        self.htmlreader = HTMLReader(pages=set(self.pages),config=self.config)
        if self.htmlsplitter is None:
            self.htmlsplitter = SemanticSplitter(config=self.config)
        return self
    
    
    def run(self):
        #create index or check if one is already created-
        for root_node , html in self.htmlreader:
            
             
            self.htmlsplitter.merge(root_node)
            self.htmlsplitter.vectorize(root_node)
            with database.get_db() as db:
                database.insert_data(db,root_node=root_node)
            
            #load data into index
            #print (qa._generate_qa(html,self.config.n))
            
        
        #eval
        #-> modify config
        #run()<