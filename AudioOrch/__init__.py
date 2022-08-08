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
from utils import SplitWavAudioMubin
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
    return tosave

def orchestrator_function(context: df.DurableOrchestrationContext):

    fileUrl = context.get_input()
    audiopath = dowload_file(fileUrl)
    split_wav = SplitWavAudioMubin(tempdir, audiopath)

    results_paths = split_wav.multiple_split(min_per_split=2)
    parallel_tasks = [context.call_activity(
        "MakeText", b) for b in results_paths]
    output = yield context.task_all(parallel_tasks)

    total_summary= list(itertools.chain.from_iterable(output))
    return total_summary


main = df.Orchestrator.create(orchestrator_function)