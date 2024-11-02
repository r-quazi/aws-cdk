
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

    # If a request body is present, parse it and insert the data into DynamoDB.
    # Handle POST requests
    if event["httpMethod"] == "POST":
        if event["body"]:
            item = json.loads(event["body"])
            logging.info(f"## Received payload: {item}")
            year = str(item["year"])
            title = str(item["title"])
            id = str(item["id"])

            # Insert the data into DynamoDB table.
            dynamodb_client.put_item(
                TableName=table,
                Item={"year": {"N": year}, "title": {"S": title}, "id": {"S": id}},
            )
            message = "Successfully inserted data you have provided!"
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": message}),
            }
        else:
            logging.info("## Received request without a payload")

            # Insert the default data into DynamoDB table.
            dynamodb_client.put_item(
                TableName=table,
                Item={
                    "year": {"N": "2012"},
                    "title": {"S": "The Amazing Spider-Man 2"},
                    "id": {"S": str(uuid.uuid4())},
                },
            )
            message = "Successfully inserted DEFAULT data!"
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": message}),
            }

    # Handle GET requests
    elif event["httpMethod"] == "GET":
        response = dynamodb_client.scan(TableName=table)
        items = response.get('Items', [])
        
        # Format the items to return as part of the response
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
    
    # Handle unsupported HTTP methods
    else:
        return {
            "statusCode": 405,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Method Not Allowed"}),
        }



# MY NOTES :
# #### STORING DATA #####
# curl -X POST \
#   https://{api-id}.execute-api.{region}.amazonaws.com/{stage}/ \
#   -H "Content-Type: application/json" \
#   -d '{
#         "year": 2023,
#         "title": "Example Title",
#         "id": "unique-id-1234"
#       }'

# #### RETRIEVING DATA #####
# curl -X GET \
#   https://{api-id}.execute-api.{region}.amazonaws.com/{stage}/

# ### You can do curl to add data to the  database #####


