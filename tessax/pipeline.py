from pydantic import BaseModel,model_validator,ConfigDict,HttpUrl,Field
from bs4 import BeautifulSoup
import typing as t
from .html_reader import HTMLReader
from .splitter import *
from .config import RAGConfig
from .node import Node
from . import database
from .qa import generate_q, generate_answers
from .splitter import SemanticSplitter,LateSplitter
from .evaluation import Evaluate

from pandas import DataFrame
from dataclasses import dataclass
import optuna
from optuna.samplers import TPESampler

__all__ = "RAGPipeline"

SPLITTERS = {
        "semantic": SemanticSplitter,
        "late": LateSplitter,  
    }
class RAGPipeline(BaseModel):
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    pages : set[HttpUrl]
    
    evaluation : Evaluate
    config : RAGConfig | None = None
    htmlsplitter : HTMLSplitter | None = None
    htmlreader : HTMLReader | None = None
    q : DataFrame | None = None
    
    config: RAGConfig = Field(default_factory=RAGConfig)
    
    
    splitter_type: t.Literal["semantic", "late"] = "semantic"

    

    @model_validator(mode="after")
    def initialize_components(self) -> "RAGPipeline":
        
        self.htmlreader = self.htmlreader or HTMLReader(pages=self.pages,config=self.config)    
        
        if self.htmlsplitter is None:
            splitter_class = SPLITTERS.get(self.splitter_type)
            if splitter_class is None:
                raise ValueError(f"Unknown splitter type: {self.splitter_type}")
            self.htmlsplitter = splitter_class(config=self.config)
        return self
    
    
    def run(self):
        
        root_node : Node
        html : BeautifulSoup
        
        database.delete_entries()
        
        
        for root_node , html in self.htmlreader:
            
             
            self.htmlsplitter.merge(root_node)
            self.htmlsplitter.vectorize(root_node)
            
            database.insert_data(root_node=root_node)
            if self.q is None:
                self.q = (generate_q(html,self.config.question_count))
             
        database.create_index()
  
  

        #generate answers
        qa = generate_answers(self.q)   

        #run metrics 
        self.evaluation.run_metrics(qa)
        
        
        #return loss
        print(qa)
        print(qa["faithfulness"].mean())
        return qa["faithfulness"].mean()



    

class Trial():
    
    def __init__(self,
                pages : set[HttpUrl],  
                evaluation : Evaluate,
                n_startup_trials : int = 2,
                n_trials : int = 10,
                q : DataFrame | None = None,
                
                ):
        self.pages = pages
        self.evaluation = evaluation
        self.n_startup_trials = n_startup_trials
        self.n_trials = n_trials
        self.q = q
    def optimize(self):
        sampler = TPESampler(n_startup_trials=self.n_startup_trials, multivariate=True, seed=42)
        study = optuna.create_study(sampler=sampler, direction='maximize',storage="postgresql://postgres:password@localhost:5432/example_db")
     
        study.optimize(self.trial, n_trials=self.n_trials)
        print("Best hyperparameters:", study.best_params)
        print("Best value:", study.best_value)
        
    def trial(self,trial):
        
        splitter_type = trial.suggest_categorical('splitter_type', ['semantic', 'late'])
        if splitter_type == 'semantic':
            simil = trial.suggest_float('simil', 0.1, 0.8)
            trial_conf = RAGConfig(simil=simil)
            
        elif splitter_type == 'late':
            chunk_size = trial.suggest_int('chunk_size', 2, 100)
            trial_conf = RAGConfig(chunk_size=chunk_size)
        pipeline = RAGPipeline(pages = self.pages,evaluation=self.evaluation,config=trial_conf,splitter_type=splitter_type,q=self.q)
        
        result = pipeline.run()
        if self.q is None:
            self.q = pipeline.q
        return  result