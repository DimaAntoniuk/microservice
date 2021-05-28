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

        get_announcements_integration = aws_apigateway.LambdaIntegration(consumer_lambda, proxy=False,
                request_templates={"application/json": '{ "statusCode": "200" }'})

        post_announcement_integration = aws_apigateway.LambdaIntegration(producer_lambda,proxy=False,
                method_responses=[MethodResponse(status_code="200")])

        announcements.add_method("GET", get_announcements_integration, api_key_required=False)
        announcements.add_method("POST", post_announcement_integration, api_key_required=False)

        # key = api.add_api_key("ApiKey",
        #     api_key_name="secret-key-name",
        #     value="secret-ley-value"
        # )