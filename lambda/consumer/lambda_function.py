import boto3
import json
import os
from botocore.exceptions import ClientError


TABLE_NAME = os.environ['TABLE_NAME']
client = boto3.resource('dynamodb')
table = client.Table(TABLE_NAME)


def lambda_handler(event, context, table=table):
    try:
        response = table.scan()
        items = response['Items']
        while 'LastEvaluetionKey' in response:
            response = table.scan(ExlusiveStartKey=response['LastEvaluetedKey'])
            items.extend(response['Items'])
    except ClientError as e:
        return {
            'statusCode': '400',
            'errorMessage': e.response['Error']['Message']
        }
    return {
        'statusCode': '200',
        'body': json.dumps(items)
    }