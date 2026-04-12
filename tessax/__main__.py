from pipeline import RAGPipeline
from config import Config
if __name__ == "__main__":
    print("Starting the application...")
    pipeline = RAGPipeline(pages=["https://www.hochschule-rhein-waal.de/de/fakultaeten/kommunikation-und-umwelt/studienangebot/bachelorstudiengaenge/medieninformatik-bsc"],config=Config(index_name="test"))
    pipeline.run()
    
    print("finished")
    
