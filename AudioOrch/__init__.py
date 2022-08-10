# This function is not intended to be invoked directly. Instead it will be
# triggered by an HTTP starter function.
# Before running this sample, please:
# - create a Durable activity function (default name is "Hello")
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging
import json
import os
import tempfile
import azure.functions as func
import azure.durable_functions as df
from .helper.utils import SplitWavAudioMubin
from moviepy.editor import *
import itertools
from azure.storage.blob import BlobServiceClient

tempdir = tempfile.gettempdir()
def dowload_file(name, tempdir = tempdir):

    blob_service_client = BlobServiceClient.from_connection_string("DefaultEndpointsProtocol=https;AccountName=aistudio9f70;AccountKey=1EtoBzcsmU6AfEQTeAKwi5oiKWVkAUU4y96DkExaY6dXZOjsWuJYtFI/19zk0ipL/iF9aD65W6JM+ASt5GayTg==;EndpointSuffix=core.windows.net")
    data_container_client = blob_service_client.get_container_client("videos")
    tosave = os.path.join(tempdir, name)
    with open(tosave, "wb") as data:
        download_stream = data_container_client.download_blob(name)
        data.write(download_stream.readall())
    return name

def upload_data(data, filename, container_name="output"):
    blob_service_client = BlobServiceClient.from_connection_string(
        "DefaultEndpointsProtocol=https;AccountName=aistudio9f70;AccountKey=1EtoBzcsmU6AfEQTeAKwi5oiKWVkAUU4y96DkExaY6dXZOjsWuJYtFI/19zk0ipL/iF9aD65W6JM+ASt5GayTg==;EndpointSuffix=core.windows.net"
    )
    data_container_client = blob_service_client.get_container_client(
        container_name)
    filename = "{}.txt".format(filename)

    blob_client = data_container_client.upload_blob(
        name=filename, data=data, overwrite=True)
    return blob_client.url

def orchestrator_function(context: df.DurableOrchestrationContext):

    fileUrl = context.get_input()
    instance_id = context.instance_id
    audiopath = dowload_file(fileUrl["url"])
    video = VideoFileClip(os.path.join(tempdir, fileUrl["url"])) # 2.
    audio = video.audio # 3.
    audiourl = fileUrl["url"].replace(".mp4", ".wav")
    audio.write_audiofile(os.path.join(tempdir, audiourl))
    split_wav = SplitWavAudioMubin(tempdir, audiourl)
    #os.mkdir(tempdir + '\\' + 'splitted')
    results_paths = split_wav.multiple_split(min_per_split=2)
    parallel_tasks = [context.call_activity(
        "MakeText", b) for b in results_paths]
    output = yield context.task_all(parallel_tasks)

    total_summary= ""
    for out in output:
        total_summary += out
    blobUrl = upload_data(total_summary,instance_id)
    return blobUrl


main = df.Orchestrator.create(orchestrator_function)