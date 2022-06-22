from time import strftime
import boto3
import os
from botocore.exceptions import ClientError
from marshmallow import ValidationError, fields, validate, Schema

def full(f):
    def wrap(*args):
        wrapped_output = f(*args) + ': '
        for arg in args:
            wrapped_output += f'{arg.__dict__}'
        return wrapped_output
    return wrap


class Announcement:
    def __init__(self, id, title, description, date):
        self.id = id
        self.title = title
        self.description = description
        self.date = date
    
    def to_json(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "date": self.date.strftime("%d-%m-%Y")
        }

    @full
    def __repr__(self):
        return f'{type(self).__name__}[{self.id}]'


class AnnouncementSchema(Schema):
    id = fields.UUID(required=True)
    title = fields.String(required=True, validate=validate.Length(min=3))
    description = fields.String(required=True, validate=validate.Length(min=10))
    date = fields.Date(required=True)

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
    schema = AnnouncementSchema()
    try:
        validated_items = schema.load(items, many=True)
        result = [Announcement(**item).to_json() for item in validated_items]
    except ValidationError as e:
        return {
            'statusCode': '400',
            'errorMessage': e.messages
        }
    return {
        'statusCode': '200',
        'body': result
    }