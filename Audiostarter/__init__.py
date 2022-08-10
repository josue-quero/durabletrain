# This function an HTTP starter function for Durable Functions.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable activity function (default name is "Hello")
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt
 
import logging
import json
import azure.functions as func
import azure.durable_functions as df


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    input = req.get_json()
    client = df.DurableOrchestrationClient(starter)
    instance_id = await client.start_new(req.route_params["functionName"], None, input)

    logging.info(f"Started orchestration with ID = '{instance_id}'.")
    
    return func.HttpResponse(json.dumps({"instance_id": instance_id, "message": "Consult your results in the GET Results API"}), status_code=200)