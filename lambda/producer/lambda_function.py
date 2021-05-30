import boto3
import uuid
import os
from datetime import date
from botocore.exceptions import ClientError


def validate_date(date):
    return date.strftime('%d-%m-%Y')


client = boto3.resource('dynamodb')
TABLE_NAME = os.environ['TABLE_NAME']


def lambda_handler(event, context):
    client = boto3.resource('dynamodb')
    table = client.Table(TABLE_NAME)
    try:
        response = table.put_item(
            Item = {
                'id': str(uuid.uuid4()),
                'title': event.get('title', ''),
                'description': event.get('description', ''),
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
        'body': 'Announcement "' + event.get('title', 'undefined') + '" posted'
    }