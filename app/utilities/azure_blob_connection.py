# Import required modules
from azure.storage.blob import BlobServiceClient
import pandas as pd
from io import BytesIO
import os
import sys


# Upload a file to Azure Blob Storage
def read_from_azure_blob_storage(connection_string, container_name, file_name):
    '''
        Input:
            * connection_string (str): A secret key required to connect to Azure Client
            * container_name (str): The container we wish to connect to/create and connect to wrt the corresponding connection string's account
            * file_name (str): The name of the location (file) in the container where the read will occur
    '''
    print(f"connection_string is: {connection_string}")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(file_name)
    blob_data = blob_client.download_blob()
    data = blob_data.readall()
    df = pd.read_csv(BytesIO(data))
    return(df)


# Show a list of blobs in a container
def show_azure_blobs(connection_string, container_name):
    '''
        Input:
            * connection_string (str): A secret key required to connect to Azure Client
            * container_name (str): The container we wish to connect to/create and connect to wrt the corresponding connection string's account

        Output:
            * blob_list (list[str]): A list of blobs in the specified azure blob container 
    '''
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    blobs_raw = container_client.list_blobs()
    blob_list = []
    for b in blobs_raw:
        blob_list.append(b.name)
    return(blob_list)