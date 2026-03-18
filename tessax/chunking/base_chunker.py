from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import MarkdownHeaderTextSplitter
from typing import Optional,List
import json
import uuid



class BaseChunking:
    def __init__(
        self,
        azure_utils : Optional[AzureUtils] = None,
        index_key : Optional[int] = 0   
    ):
        self.azure_utils = azure_utils or AzureUtils()
        self.azure_openai = AzureOpenAI()
        self.deduplication_tool = DeduplicationTool()
        self.index_key = index_key
    def splitStore(self,loaded_data,url,url_bool,titel) -> None:

        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        text_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        recursive_text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=int(config.CHUNK_SIZE),chunk_overlap=int(config.CHUNK_OVERLAP))
        if url_bool:
            splits = text_splitter.split_text(loaded_data)
        else:
            splits = text_splitter.split_text(loaded_data[0].page_content)
        splits = recursive_text_splitter.split_documents(splits)
    
        for split in splits:
            self.pushToVector(titel+" "+str(split.page_content),url,'txt')
        
    def extract_html(self,soup,url):
        text = soup.get_text()
        if config.TITEL == "True":
            titel = self.azure_openai.generate_titel(soup.get_text()) 
            print(titel)

        else:
            titel = ""
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        self.splitStore(text,url,True,titel)

    @staticmethod
    def setup_html(soup):
        for script in soup(["script", "style"]):
            script.extract() 
        for each in ['header', 'footer']:
            s = soup.find(each)
            if s is not None:
                s.extract()
        return soup
    
    def pushToVector(
            self,
            content,
            url,
            type,
            window : Optional[List[str]] = [],
            summary : Optional[str] = ""
            ):
        embedded_content = self.azure_utils.create_embedding(content +" "+ summary)
        
        
        myuuid = uuid.uuid4()
        tmp_doc={"id" : str(myuuid),
                        "content": content, 
                        "type":type,
                        "source":url,
                        "metadata": json.dumps(window),
                        "content_vector": embedded_content}
      

        config.SEARCH_CLIENT.upload_documents([tmp_doc])  
        print("pushed")