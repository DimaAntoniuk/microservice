import boto3
import uuid
import os
from botocore.exceptions import ClientError


client = boto3.resource('dynamodb')
TABLE_NAME = os.environ['TABLE_NAME']


def lambda_handler(event, context):
    client = boto3.resource('dynamodb')
    table = client.Table(TABLE_NAME)
    try:
        response = table.put_item(
            Item = {
                'uuid': uuid.uuid4(),
                'title': event.get('title', ''),
                'description': event.get('description', ''),
                'date': event.get('date', '')            
            }
        )
    except ClientError as e:
        return {
            'statusCode': '404',
            'errorMessage': e.response['Error']['Message']
        }

    return {
        'statusCode': response['ResponseMetadata']['HTTPStatusCode'],
        'body': 'Announcement \"' + event.get('title', 'undefined') + '\" posted'
    }