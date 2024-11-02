#importing cdk
import aws_cdk as cdk  

#importing  ApigwHttpApiLambdaDynamodbStepFunctionPythonCdkStack from stack/apigw_http_api_lambda_dynamodb_python_step_function_cdk_stack.py python file.
from stacks.apigw_http_api_lambda_dynamodb_step_function_python_cdk_stack import ApigwHttpApiLambdaDynamodbStepFunctionPythonCdkStack   

#creating app instance
app = cdk.App()   

#add instance of ApigwHttpApiLambdaDynamodbStepFunctionPythonCdkStack to the app instance.
ApigwHttpApiLambdaDynamodbStepFunctionPythonCdkStack(app, "ApigwHttpApiLambdaDynamodbStepFunctionPythonCdkStack")  

#creating cloud formation
app.synth()  
