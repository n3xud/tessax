from .pipeline import RAGPipeline, Trial
from .config import RAGConfig
from .evaluation import Evaluate, Faithfulness , ContextRelevance

if __name__ == "__main__":
    print("Starting the application...")
    evaluate = Evaluate([Faithfulness(),ContextRelevance()])
    conf = RAGConfig()
    pipeline = RAGPipeline(pages=["https://www.ny.gov/services/apply-cooling-assistance"],evaluation=evaluate,splitter_type="late")
    #trial = Trial(pages=["https://www.ny.gov/services/apply-cooling-assistance"],evaluation=evaluate)
    
    pipeline.run()
    #trial.optimize()
    print("finished")
    
