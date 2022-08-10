import logging

import azure.functions as func
from azure.storage.blob import BlobServiceClient

def get_url(name):

    blob_service_client = BlobServiceClient.from_connection_string("DefaultEndpointsProtocol=https;AccountName=aistudio9f70;AccountKey=1EtoBzcsmU6AfEQTeAKwi5oiKWVkAUU4y96DkExaY6dXZOjsWuJYtFI/19zk0ipL/iF9aD65W6JM+ASt5GayTg==;EndpointSuffix=core.windows.net")
    data_container_client = blob_service_client.get_container_client("output")
    files = data_container_client.list_blobs()
    file_list = [blob.name for blob in files]
    if name + ".txt" in file_list:
        blob_client = blob_service_client.get_blob_client(container="output", blob=name + ".txt")
        url = blob_client.url

    else:
        url = ""

    return url

def main(req: func.HttpRequest) -> func.HttpResponse:
    name = req.params.get('url')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('url')

    if name:
        url = get_url(name)
        if url != "":
            return func.HttpResponse(url)
        else:
            return func.HttpResponse("La transcripción sigue en proceso")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
