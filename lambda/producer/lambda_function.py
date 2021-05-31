import boto3
import uuid
import os
from datetime import date
from botocore.exceptions import ClientError


def validate_date(date):
    return date.strftime('%d-%m-%Y')


TABLE_NAME = os.environ['TABLE_NAME']
client = boto3.resource('dynamodb')
table = client.Table(TABLE_NAME)


def lambda_handler(event, context):
    try:
        response = table.put_item(
            Item = {
                'id': str(uuid.uuid4()),
                'title': event['queryStringParameters']['title'],
                'description': event['queryStringParameters']['description'],
                'date': validate_date(date.today())          
            }
        )
    except ClientError as e:
        return {
            'statusCode': '400',
            'errorMessage': e.response['Error']['Message']
        }

    return {
        'statusCode': '200',
        'body': 'Announcement "' + event['queryStringParameters']['title'] + '" posted'
    }