import boto3
import uuid
import os
from datetime import date
from botocore.exceptions import ClientError
from marshmallow import ValidationError
from marshmallow import fields, validate, Schema


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
    
    @full
    def __repr__(self):
        return f'{type(self).__name__}[{self.id}]'


class AnnouncementSchema(Schema):
    id = fields.UUID(required=True, validate=validate.Regexp(r'^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\\Z'))
    title = fields.String(required=True, validate=validate.Length(min=3))
    description = fields.String(required=True, validate=validate.Length(min=10))
    date = fields.Date(required=True)


def validate_date(date):
    return date.strftime('%d-%m-%Y')


TABLE_NAME = os.environ['TABLE_NAME']
client = boto3.resource('dynamodb')
table = client.Table(TABLE_NAME)


def lambda_handler(event, context, table=table):

    announcement = Announcement(id=uuid.uuid4(), 
            title=event.get('title', '-'),
            description=event.get('description', '-'),
            date=date.today())
    schema = AnnouncementSchema()
    
    try:
        validated_announcement = schema.dump(announcement)
    except ValidationError as e:
        return {
            'statusCode': '400',
            'errorMessage': e.messages
        }
    
    try:
        response = table.put_item(Item=validated_announcement)
    except ClientError as e:
        return {
            'statusCode': '400',
            'errorMessage': e.response['Error']['Message']
        }
    
    return {
        'statusCode': '200',
        'body': 'Announcement "' + event['title'] + '" posted'
    }