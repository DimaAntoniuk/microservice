import pytest, re
import boto3
import pytest
import json
import os

from moto import mock_dynamodb2


def valid_uuid(uuid):
    regex = re.compile(
        '^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\\Z',
        re.I
    )
    match = regex.match(uuid)
    return bool(match)


TABLE_NAME = "announcements"
os.environ['TABLE_NAME'] = "announcements"


from .consumer import lambda_function  as consumer_lambda
from .producer import lambda_function  as producer_lambda


@pytest.fixture
def use_moto():
    @mock_dynamodb2
    def dynamodb_client():
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-3')

        # Create the table
        dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'title',
                    'KeyType': 'RANGE'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'title',
                    'AttributeType': 'S'
                },
            ]
        )
        return dynamodb
    return dynamodb_client


@pytest.fixture
def fake_use_moto():
    @mock_dynamodb2
    def dynamodb_client():
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

        # Create the table
        dynamodb.create_table(
            TableName='fake',
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'title',
                    'KeyType': 'RANGE'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'title',
                    'AttributeType': 'S'
                },
            ]
        )
        return dynamodb
    return dynamodb_client


@mock_dynamodb2
def test_consumer_handler_for_failure(fake_use_moto):
    fake_use_moto()
    event = {
        "statusCode": "200"
    }

    return_data = consumer_lambda.lambda_handler(event, "")
    assert return_data['statusCode'] == '400'
    assert isinstance(return_data['errorMessage'], str)


@mock_dynamodb2
def test_consumer_handler_for_valid_response(use_moto):
    use_moto()
    table = boto3.resource('dynamodb', region_name='eu-west-3').Table(TABLE_NAME)
    table.put_item(
        Item={
            'id': "test",
            'title': "test",
            'description': "test",
            'date': "test"
        }
    )
    event = {
        "queryStringParameters": {
            "title":"dummy",
            "description": "dummy"
        }
    }

    return_data = producer_lambda.lambda_handler(event, "")

    assert return_data['statusCode'] == '200'
    assert return_data['body'] == 'Announcement "' + event['queryStringParameters']['title'] + '" posted'

    event = {
        "statusCode": "200"
    }

    return_data = consumer_lambda.lambda_handler(event, "")
    print(str(return_data))

    assert return_data['statusCode'] == '200'
    body = json.loads(return_data['body'])
    assert body[0]['id'] == 'test'
    assert body[0]['title'] == 'test'
    assert body[0]['description'] == 'test'
    assert body[0]['date'] == 'test'


@mock_dynamodb2
def test_producer_handler_for_failure(fake_use_moto):
    fake_use_moto()
    event = {
        "queryStringParameters": {
            "title": "dummy",
            "description": "dummy"
        }
    }

    return_data = producer_lambda.lambda_handler(event, "")
    assert return_data['statusCode'] == '400'
    assert isinstance(return_data['errorMessage'], str)


@mock_dynamodb2
def test_producer_handler_for_valid_response(use_moto):
    use_moto()

    event = {
        "queryStringParameters": {
            "title":"dummy",
            "description": "dummy"
        }
    }

    return_data = producer_lambda.lambda_handler(event, "")

    assert return_data['statusCode'] == '200'
    assert return_data['body'] == 'Announcement "' + event['queryStringParameters']['title'] + '" posted'

@mock_dynamodb2
def test_full_microservice(use_moto):
    use_moto()
    event = {
        "queryStringParameters": {
            "title":"test",
            "description": "test"
        }
    }

    return_data = producer_lambda.lambda_handler(event, "")

    assert return_data['statusCode'] == '200'
    assert return_data['body'] == 'Announcement "' + event['queryStringParameters']['title'] + '" posted'

    event = {
        "statusCode": "200"
    }

    return_data = consumer_lambda.lambda_handler(event, "")
    print(str(return_data))

    assert return_data['statusCode'] == '200'
    body = json.loads(return_data['body'])
    assert valid_uuid(body[0]['id'])
    assert body[0]['title'] == 'test'
    assert body[0]['description'] == 'test'
    assert isinstance(body[0]['date'], str)