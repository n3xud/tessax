import os
from pydantic import BaseModel,model_validator,ConfigDict,HttpUrl,Field
from bs4 import BeautifulSoup
import typing as t
from .html_reader import HTMLReader
from .config import ChunkModes,cfg,cfg_trial
from .node import Node
from . import database
from .qa import generate_q, generate_answers
from .chunker import Chunker
from .evaluation import Evaluate

import time

from pandas import DataFrame
import pandas
import optuna
from optuna.samplers import TPESampler
from loguru import logger
__all__ = "RAGPipeline"





class RAGPipeline(BaseModel):
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    page : HttpUrl
    evaluation : Evaluate | None = None
    
    htmlchunker : Chunker  | None = None
    htmlreader : HTMLReader | None = None
    q : DataFrame | None = None
    html : BeautifulSoup | None = None
    
    
    
    

    @model_validator(mode="after")
    def initialize_components(self) -> "RAGPipeline":
        
        self.htmlreader = self.htmlreader or HTMLReader(page=self.page)    
        
        self.htmlchunker = self.htmlchunker or Chunker() 
            
        return self
    
    
    def run(self):
        
        root_node : Node
        html : BeautifulSoup
        
        database.delete_entries()
        
        scores = []
        
        start = time.perf_counter()
        if self.html is None :
            root_node , html = self.htmlreader.crawl()
            self.html = html
        else:
            root_node , html = self.htmlreader.crawl(html = self.html)  
        end = time.perf_counter()
        print(f"Request Dauer: {end - start:.4f} Sekunden") 
            
            
            
        start = time.perf_counter()   
        self.htmlchunker.process_vectorization(root_node)
        end = time.perf_counter()
        print(f"Vektor Dauer: {end - start:.4f} Sekunden") 
        
        start = time.perf_counter()
        database.insert_data(root_node=root_node)
        
        end = time.perf_counter()
        print(f"Index Dauer: {end - start:.4f} Sekunden") 
        
        
        if self.q is None or cfg_trial.fixed:
            start = time.perf_counter()
            self.q = (generate_q(html))
            end = time.perf_counter()
            print(f"QA Generation Dauer: {end - start:.4f} Sekunden") 
        database.create_index()
        #generate answers
        start = time.perf_counter()
        qa = generate_answers(self.q)   
        end = time.perf_counter()
        print(f"Antwort Dauer: {end - start:.4f} Sekunden") 
        #run metrics 
        start = time.perf_counter()
        if self.evaluation:
            scores = self.evaluation.run_metrics(qa)
        end = time.perf_counter()
        print(f"Evaluation Dauer: {end - start:.4f} Sekunden") 
        print(qa)
        return scores

class Trial():
    
    def __init__(self,
                pages : HttpUrl | str,  
                evaluation : Evaluate,
                
                q : DataFrame | None = None,
                html : BeautifulSoup | None = None,
                ):
       
        if isinstance(pages,str):
            df = pandas.read_csv(pages,header=None)
            self.pages = df.iloc[:, 0].dropna().tolist()
        else: 
            self.pages = [pages]
        self.evaluation = evaluation
        self.n_startup_trials = cfg_trial.startup_trials
        self.n_trials = cfg_trial.trials
        self.q = q
        self.html = html
        
    def optimize(self):
        
        sampler = TPESampler(n_startup_trials=self.n_startup_trials, multivariate=False, seed=42)
        
        eval_names = [evaluation.__name__ for evaluation in self.evaluation.metrics]
        directions = ["maximize"] * len(eval_names)
        study = optuna.create_study(
            sampler=sampler, 
            directions=directions,
            storage="postgresql://postgres:password@localhost:5432/example_db",
            study_name=cfg_trial.study_name,
            load_if_exists=True)
        
        
        study.set_metric_names(eval_names)
        
        for page in self.pages:
            self.current_page = page
            self.q = None
            self.html = None
            logger.info("Analyzing: {} ", self.current_page)

            if cfg_trial.fixed:

                study.enqueue_trial(cfg_trial.fixed_params)
                n_trials = 1
            else:
                n_trials = cfg_trial.trials

            study.optimize(self.trial, n_trials=n_trials,catch=(
            Exception,
        ))
        

        
       
        df = study.trials_dataframe()
        file_path = cfg_trial.study_name +  '.csv'
        file_exists = os.path.exists(file_path)
        df.to_csv(file_path, mode='a', header=not file_exists, index=False)

    def trial(self,trial):
        start = time.perf_counter()
        chunk_mode_str = trial.suggest_categorical('chunk_mode', [ChunkModes.FIXED_CHUNKING.value, ChunkModes.SEMANTIC_CHUNKING.value])
        
        context_parents  = trial.suggest_categorical('context_parents', [True,False])
        retrieval_count = trial.suggest_int('retrieval_count', 2,10)
        
        cfg.add_parent_context = context_parents
        cfg.retrieval_count    = retrieval_count
        
        chunk_mode = ChunkModes(chunk_mode_str)
        
        if chunk_mode == ChunkModes.FIXED_CHUNKING:
            chunk_size = trial.suggest_int('chunk_size', 64, 1024)
            cfg.chunk_size = chunk_size
        elif chunk_mode == ChunkModes.SEMANTIC_CHUNKING:
            simil = trial.suggest_float('simil', 0.1, 0.9)
            cfg.simil = simil
            
        
        cfg.chunk_mode = chunk_mode
        
        
        trial.set_user_attr("page", str(self.current_page))
        
        pipeline = RAGPipeline(page = self.current_page,evaluation=self.evaluation,q=self.q,html=self.html)
        
        result = pipeline.run()
        if self.q is None:
            self.q = pipeline.q
            
        if self.html is None:
            self.html = pipeline.html
            
        end = time.perf_counter()
        print(f"Trial Dauer: {end - start:.4f} Sekunden") 
        return  result