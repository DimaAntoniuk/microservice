from aws_cdk import core
from config import config
from microservice.microservice_stack import MicroserviceStack


app = core.App()
MicroserviceStack(app, "MicroserviceStack", env=core.Environment(account=config.ACCOUNT_ID, region=config.REGION))

app.synth()
