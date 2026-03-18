import milestone_ai.config as config

import requests
import time

import pandas as pd
import json
from openai import AzureOpenAI as opai
from azure.identity import DefaultAzureCredential
import numpy as np
from milestone_ai.index.logging import Logger
from typing import Dict, List, Optional, Tuple, cast
from pydantic import BaseModel, Field

class TableInformation(BaseModel):
    table_header:list[str]  = Field(...,description="Generiere Überschriften für jede Spalte in der Tabelle. Always include empty colums.")
    table_summary:str       = Field(...,description="Schreibe eine ausführliche Zusammenfassung fuer die Tabelle in ein paar Sätzen. Verwende moeglichst viele Informationen.")


class AzureOpenAI:

    def __init__(self,logger:Optional[Logger] = None) -> None:
        self.logger = logger or Logger()
        self.header = {
            "Content-Type": "application/json",
            "api-key":  config.AZURE_OPENAI_API_KEY,
        }

    def send_to_openai(self,payload):
        for i in range(10):
            try:
                response = requests.post(config.GPT4V_ENDPOINT, headers=self.header, json=payload)
                if response.status_code == 200:
                    break
                else:
                    print("warning")
                    time.sleep(20)
            except Exception as e:
                pass
        answer = response.json()
        return(answer["choices"][0]["message"]["content"])
    

    def image_to_text(self,user_prompt,image_url):
        

        # Payload for the request
        payload = {
        "messages": [
            {
            "role": "system",
            "content": [
                {
                "type": "text",
                "text": ""
                }
            ]
            },
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": user_prompt
                },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        } 
            ]
            }
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 800
        }
        
        return self.send_to_openai(payload)

    def table_to_text_new(self,df,blob_name_string,name):
        print("In: table_to_text_new")
        
        client = opai(
            api_key= config.AZURE_OPENAI_API_KEY ,#"f4aea1ea10b94117962ed93707849b1c",
            api_version= config.OPENAI_API_VERSION ,#"2024-07-01-preview",
            azure_endpoint = config.AZURE_OPENAI_ENDPOINT#"https://oai-rag-dev-sweden.openai.azure.com/",
        )
        print("In: table_to_text_new")
        
        
       

        response = client.beta.chat.completions.parse(
            model=config.MODEL,
            messages=[
                        {"role": "system", "content": f""},
                        {"role": "user", "content": f"{df.iloc[0:20].to_html()}"},
                    ],
            response_format = TableInformation,
            temperature= 0.0

        )
        print("In: table_to_text_new")
        response= response.choices[0].message.parsed

        # Handle function calls

        tabelcolums = response.table_header
       

        print(tabelcolums)

        len_gpt_header_len = len(tabelcolums[1:]) 
        len_dif = len(df.columns) - len_gpt_header_len
        # if len_dif < 0:
        #     print(len_dif)
        #     tabelcolums = tabelcolums[1:len(df.columns)+1]
        # elif len_dif > 0:
        #     print(len_dif)
        #     #tabelcolums = tabelcolums.extend(['']*len_dif)
        # else:
        #     print(len_dif)
        #     tabelcolums = tabelcolums[1:]

        print(tabelcolums)
        


        if tabelcolums:
            df.columns = tabelcolums
            print(df.columns)
            self.logger._save_logging(blob_name_string+ "Excelsheetname: " + name,table_headings_createt=True) 
        else:
            self.logger._save_logging(blob_name_string+ "Excelsheetname: " + name,table_headings_createt=False) 
            print("no tabelcolums found")


        # Process the model's response
        response_summery_message = response.table_summary

        print(response_summery_message)

        df.replace(' ',np.NaN,inplace= True)
        df.dropna(axis = 0, how = 'all', inplace = True)

        row_count_per_chunk = 12
        step_size = 8

        steps_to_go = int((len(df)-row_count_per_chunk)/(row_count_per_chunk-step_size))
        if steps_to_go < 0:
            steps_to_go = 0

        responsearray = []

        for i in range(steps_to_go+2):
            html_tabel_text = df.iloc[i*(row_count_per_chunk-step_size):i*(row_count_per_chunk-step_size)+row_count_per_chunk].to_html()
            content_string = response_summery_message + "\n" + html_tabel_text
            responsearray.append(content_string)
            #print(response_summery_message + "\n" + html_tabel_text)

        return responsearray
    @staticmethod
    def generate_titel(txt):
        
        client = opai(
        azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
        api_version="2024-02-01",
        api_key=config.AZURE_OPENAI_API_KEY
        )
            
        completion = client.chat.completions.create(
        model=config.MODEL,
        messages=[
            {
                "role": "system",
                "content": [
                    {
                "type": "text",
                "text": "You are an AI assistant that helps people find information."
                    }
            ],
            
                "role": "user",
                "content": txt+ " Generiere einen Titel für den gegebenen Text",
            },
        ],
        
        )
            
        
        return(completion.choices[0].message.content)
    
    @staticmethod
    def contextual_generation(chunk,document):
        client = opai(
        azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
        api_version="2024-02-01",
        api_key=config.AZURE_OPENAI_API_KEY
        )
            
        completion = client.chat.completions.create(
        model=config.MODEL,
        messages=[
            {
                "role": "system",
                "content": [
                    {
                "type": "text",
                "text": "You are an AI assistant that helps people find information."
                    }
            ],
            
                "role": "user",
                "content": 
                    "<document>" 
                    f"{document}"
                    "</document>" 
                    "Hier ist der Abschnitt, den wir innerhalb des gesamten Dokuments einordnen möchten"
                    "<chunk>"
                    f"{chunk}" 
                    "</chunk>" 
                    "Bitte geben Sie einen kurzen, prägnanten Kontext, um diesen Abschnitt innerhalb des gesamten Dokuments einzuordnen, um die Suchabrufbarkeit des Abschnitts zu verbessern. Antworten Sie nur mit dem prägnanten Kontext und nichts anderem.",
                
            },
        ],
        
        )
        print("total tokens:"+str(completion.usage.total_tokens)) 
        return(completion.choices[0].message.content)