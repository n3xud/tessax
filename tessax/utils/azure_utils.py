import milestone_ai.config as config


from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from azure.storage.blob import  BlobClient, ContainerClient
from datetime import timedelta, datetime

class AzureUtils():
    @staticmethod
    def create_embedding(content):
        return config.EMB_CLIENT.embeddings.create(input = [content], model = config.EMBEDDING_MODEL).data[0].embedding
    
    @staticmethod
    def get_blob_service_client_connection():
        connection_string = "DefaultEndpointsProtocol=https;AccountName="+config.BLOB_NAME+";AccountKey="+config.BLOB_API_KEY+";EndpointSuffix=core.windows.net"
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        return blob_service_client

    def sas_generation(self,container_name,blob_name,client):
        """
            container_name = group of blobs
        """

        sas_token = self.generateSAS(container_name,blob_name,client)
        sas_url = 'https://' + client.account_name + '.blob.core.windows.net/' + container_name + '/' + blob_name + '?' + sas_token
        return sas_url
    
    @staticmethod
    def generateSAS(container_name,blob_name,client):
        sas_token = generate_blob_sas(account_name=client.account_name,
                                container_name=container_name,
                                blob_name=blob_name,
                                account_key=config.BLOB_API_KEY,
                                permission=BlobSasPermissions(read=True),
                                expiry=datetime.now() + timedelta(minutes=4))
        return sas_token
