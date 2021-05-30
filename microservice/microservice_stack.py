from aws_cdk import (
    core,
    aws_lambda,
    aws_dynamodb,
    aws_events,
    aws_events_targets,
    aws_apigateway
)
from config import config


class MicroserviceStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # create dynamo table
        announcements_table = aws_dynamodb.Table(
            self, config.TABLE_NAME,
            partition_key=aws_dynamodb.Attribute(
                name="id",
                type=aws_dynamodb.AttributeType.STRING
            ),
            sort_key=aws_dynamodb.Attribute(
                name='title',
                type=aws_dynamodb.AttributeType.STRING
            )
        )

        # create producer lambda function
        producer_lambda = aws_lambda.Function(self, "producer_lambda_function",
                                              runtime=aws_lambda.Runtime.PYTHON_3_8,
                                              handler="lambda_function.lambda_handler",
                                              code=aws_lambda.Code.asset("./lambda/producer"))

        producer_lambda.add_environment("TABLE_NAME", announcements_table.table_name)

        # grant permission to lambda to write to demo table
        announcements_table.grant_write_data(producer_lambda)

        # create consumer lambda function
        consumer_lambda = aws_lambda.Function(self, "consumer_lambda_function",
                                              runtime=aws_lambda.Runtime.PYTHON_3_8,
                                              handler="lambda_function.lambda_handler",
                                              code=aws_lambda.Code.asset("./lambda/consumer"))

        consumer_lambda.add_environment("TABLE_NAME", announcements_table.table_name)

        # grant permission to lambda to read from demo table
        announcements_table.grant_read_data(consumer_lambda)

        api = aws_apigateway.RestApi(self, "announcement-api",
                  rest_api_name="Announcement Service",
                  description="Announcements.")
        
        announcements = api.root.add_resource("announcements")

        consumer_response_model = api.add_model("ConsumerResponseModel",
            content_type="application/json",
            model_name="ResponseModel",
            schema={
                "type": "object",
                "properties": {
                    "statusCode": {"type": "string"},
                    "body": {"type": "object"}
                }
            }
        )

        producer_response_model = api.add_model("ProducerResponseModel",
            content_type="application/json",
            model_name="ResponseModel",
            schema={
                "title": "producerResponse",
                "type": {"type": "object"},
                "properties": {
                    "statusCode": {"type": "string"},
                    "body": {"type": "string"}
                }
            }
        )

        error_response_model = api.add_model("ErrorResponseModel",
            content_type="application/json",
            model_name="ErrorResponseModel",
            schema={
                "title": "errorResponse",
                "type": "object",
                "properties": {
                    "statusCode": {"type": "string"},
                    "errorMessage": {"type": "string"}
                }
            }
        )

        get_announcements_integration = aws_apigateway.LambdaIntegration(consumer_lambda, proxy=False,
                request_templates={"application/json": '{ "statusCode": "200" }'},
                integration_responses=[{
                    "statusCode": "200",
                    "body": {"type": "object"}
                }, {
                    "statusCode": "400",
                    "errorMessage": {"type": "string"}
                }])

        post_announcement_integration = aws_apigateway.LambdaIntegration(producer_lambda,proxy=False,
                integration_responses=[{
                    "statusCode": "200",
                    "body": {"type": "string"}
                }, {
                    "statusCode": "400",
                    "errorMessage": {"type": "string"}
                }],
                )

        announcements.add_method("GET", get_announcements_integration, api_key_required=False,
                method_responses=[{
                    "status_code": "200",
                    "response_parameters": {
                        "method.response.header._content-_type": True,
                        "method.response.header._access-_control-_allow-_origin": True,
                        "method.response.header._access-_control-_allow-_credentials": True
                    },
                    "response_models": {"application/json": consumer_response_model}
                }, {
                    "status_code": "400",
                    "response_parameters": {
                        "method.response.header._content-_type": True,
                        "method.response.header._access-_control-_allow-_origin": True,
                        "method.response.header._access-_control-_allow-_credentials": True
                    },
                    "response_models": {"application/json": error_response_model}
                }])
        announcements.add_method("POST", post_announcement_integration, api_key_required=True,
                request_parameters={
                    "method.request.querystring.title": True,
                    "method.request.querystring.description": True
                },
                method_responses=[{
                    "status_code": "200",
                    "response_parameters": {
                        "method.response.header._content-_type": True,
                        "method.response.header._access-_control-_allow-_origin": True,
                        "method.response.header._access-_control-_allow-_credentials": True
                    },
                    "response_models": {"application/json": producer_response_model}
                }, {
                    "status_code": "400",
                    "response_parameters": {
                        "method.response.header._content-_type": True,
                        "method.response.header._access-_control-_allow-_origin": True,
                        "method.response.header._access-_control-_allow-_credentials": True
                    },
                    "response_models": {"application/json": error_response_model}
                }])

        key = api.add_api_key("MyApiKey")

        plan = api.add_usage_plan('UsagePlan', name='MyPlan', api_key=key)