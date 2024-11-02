

# Thsi is the the main entry point for the Lambda function.
#  This file contains code that handles HTTP requests, 
# interacts with a DynamoDB table, 
# and logs information about the request and response

import boto3   # to interact with dynamodb
import os      # to access environment variables
import json    # For parsing JSON  data
import logging # for logging information during execution  
import uuid    # for generating unique identifier

# Initialize logger with INFO level to capture logs of the function execution.
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize dynamodb client using boto3.client method to connect to DynamoDB
dynamodb_client = boto3.client("dynamodb")

# The main function that handles the HTTP request.
# event contains information about http request
# context contains runtime information about tlambda function.
def handler(event, context):
    table = os.environ.get("TABLE_NAME")
    logging.info(f"## Loaded table name from environment variable TABLE_NAME: {table}")
    logging.info(f"## Received event: {json.dumps(event)}")

    # Check if the event is from API Gateway or Step Functions
    if "httpMethod" in event:
        # Handle API Gateway requests
        return handle_api_gateway_request(event, table)
    else:
        # Handle Step Functions direct invocation
        return handle_step_functions_request(event, table)


# Function to handle Step Functions direct invocation
def handle_api_gateway_request(event, table):
    if event["httpMethod"] == "POST":
        if event.get("body"):
            item = json.loads(event["body"])
            logging.info(f"## Received payload: {item}")
            year = str(item["year"])
            title = str(item["title"])
            id = str(item["id"])

            dynamodb_client.put_item(
                TableName=table,
                Item={"year": {"N": year}, "title": {"S": title}, "id": {"S": id}},
            )
            message = "Successfully inserted data you have provided!"
        else:
            logging.info("## Received request without a payload")
            dynamodb_client.put_item(
                TableName=table,
                Item={
                    "year": {"N": "2024"},
                    "title": {"S": "The title here, Added by AWS Lambda, and invoked by AWS API Gateway."},
                    "id": {"S": str(uuid.uuid4())},
                },
            )
            message = "Successfully inserted DEFAULT data!"

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": message}),
        }

    elif event["httpMethod"] == "GET":
        response = dynamodb_client.scan(TableName=table)
        items = response.get('Items', [])
        formatted_items = [
            {
                'year': item['year']['N'],
                'title': item['title']['S'],
                'id': item['id']['S']
            } for item in items
        ]
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"items": formatted_items}),
        }
    
    else:
        return {
            "statusCode": 405,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Method Not Allowed"}),
        }

def handle_step_functions_request(event, table):
    try:
        # Default behavior for Step Functions - insert a record
        # You can modify this based on your Step Functions use case
        item = {
            "year": {"N": str(event.get("year", 2024))},
            "title": {"S": event.get("title", "Default Step Functions Title")},
            "id": {"S": event.get("id", str(uuid.uuid4()))}
        }
        
        dynamodb_client.put_item(
            TableName=table,
            Item=item
        )
        
        return {
            "statusCode": 200,
            "message": "Successfully inserted data from Step Functions",
            "item": {
                "year": item["year"]["N"],
                "title": item["title"]["S"],
                "id": item["id"]["S"]
            }
        }
    except Exception as e:
        logger.error(f"Error processing Step Functions request: {str(e)}")
        raise










# # MY NOTES :
# # #### STORING DATA #####
# # curl -X POST \
# #   https://{api-id}.execute-api.{region}.amazonaws.com/{stage}/ \
# #   -H "Content-Type: application/json" \
# #   -d '{
# #         "year": 2023,
# #         "title": "Example Title",
# #         "id": "unique-id-1234"
# #       }'

# # #### RETRIEVING DATA #####
# # curl -X GET \
# #   https://{api-id}.execute-api.{region}.amazonaws.com/{stage}/

# # ### You can do curl to add data to the  database #####
