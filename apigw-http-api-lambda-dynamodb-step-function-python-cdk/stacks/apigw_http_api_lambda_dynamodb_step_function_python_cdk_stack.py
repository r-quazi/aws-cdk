import os
from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb_,
    aws_lambda as lambda_,
    aws_apigateway as apigw_,
    aws_ec2 as ec2,
    aws_iam as iam,
    Duration,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,   
)

from constructs import Construct

TABLE_NAME = "demo_table"


class ApigwHttpApiLambdaDynamodbStepFunctionPythonCdkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC
        vpc = ec2.Vpc(
            self,
            "Ingress",
            cidr="10.1.0.0/16",
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Private-Subnet", subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                )
            ],
        )
        
        # Create VPC endpoint
        dynamo_db_endpoint = ec2.GatewayVpcEndpoint(
            self,
            "DynamoDBVpce",
            service=ec2.GatewayVpcEndpointAwsService.DYNAMODB,
            vpc=vpc,
        )

        # This allows to customize the endpoint policy
        dynamo_db_endpoint.add_to_policy(
            iam.PolicyStatement(  # Restrict to listing and describing tables
                principals=[iam.AnyPrincipal()],
                actions=[                
                "dynamodb:DescribeStream",
                "dynamodb:DescribeTable",
                "dynamodb:Get*",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:CreateTable",
                "dynamodb:Delete*",
                "dynamodb:Update*",
                "dynamodb:PutItem"],
                resources=["*"],
            )
        )

        # Create DynamoDb Table
        demo_table = dynamodb_.Table(
            self,
            TABLE_NAME,
            partition_key=dynamodb_.Attribute(
                name="id", type=dynamodb_.AttributeType.STRING
            ),
        )

        # Create the Lambda function to receive the request
        api_hanlder = lambda_.Function(
            self,
            "ApiHandler",
            function_name="apigw_handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("lambda/apigw-handler"),
            handler="index.handler",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            memory_size=1024,
            timeout=Duration.minutes(5),
        )

        # grant permission to lambda to write to demo table
        demo_table.grant_write_data(api_hanlder)
        demo_table.grant_read_data(api_hanlder)
        api_hanlder.add_environment("TABLE_NAME", demo_table.table_name)

        # Create API Gateway
        apigw_.LambdaRestApi(
            self,
            "Endpoint",
            handler=api_hanlder,
        )

        invoke_lambda_task = tasks.LambdaInvoke(
            self,
            "Invoke Lambda",
            lambda_function=api_hanlder,
            payload=sfn.TaskInput.from_object({
                "year": 2024,
                "title": " Title here, Added by AWS Lambda and Invoked by AWS Step Functions. ",  
            }),
            output_path="$.Payload"
        )                   

        # Create a Step Function State Machine
        state_machine = sfn.StateMachine(
            self,
            "StateMachine",
            definition=invoke_lambda_task,
            timeout=Duration.minutes(5)  # Timeout for the state machine
        )

        # Grant permission to the Step Function to invoke the Lambda function
        api_hanlder.grant_invoke(state_machine)
