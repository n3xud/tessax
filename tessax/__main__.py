from .pipeline import Trial

from .evaluation import Evaluate, Faithfulness ,ContextRecall ,ContextPrecision,AnswerCorrectness

if __name__ == "__main__":
    print("Starting the application...")
    evaluate = Evaluate([Faithfulness,AnswerCorrectness,ContextRecall,ContextPrecision])

    #pipeline = RAGPipeline(pages=["https://www.hochschule-rhein-waal.de/de/fakultaeten/kommunikation-und-umwelt/studienangebot/bachelorstudiengaenge/medieninformatik-bsc"],evaluation=evaluate)
    trial = Trial(pages="selected_sites.csv",evaluation=evaluate)
    
    #stats = pipeline.run()
    trial.optimize()
    
    
    
