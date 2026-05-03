from .pipeline import RAGPipeline, Trial
from .config import RAGConfig
from .evaluation import Evaluate, Faithfulness , ContextRelevance

if __name__ == "__main__":
    print("Starting the application...")
    evaluate = Evaluate([Faithfulness(),])
    conf = RAGConfig()
    #pipeline = RAGPipeline(pages=["https://www.hochschule-rhein-waal.de/de/fakultaeten/kommunikation-und-umwelt/studienangebot/bachelorstudiengaenge/medieninformatik-bsc"],evaluation=evaluate,splitter_type="late")
    trial = Trial(pages=["https://www.hochschule-rhein-waal.de/de/fakultaeten/kommunikation-und-umwelt/studienangebot/bachelorstudiengaenge/medieninformatik-bsc"],evaluation=evaluate)
    
    #pipeline.run()
    trial.optimize()
    print("finished")
    
