
# Welcome to Announcement Microservice project!

To work with this project it is mandatory to pass initialization tutorial for AWS CLI and CDK.

## Useful links

 * [`AWS CLI`](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)
 * [`AWS CDK`](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html)

## Change deployable account according to awscli configuration

Edit `ACCOUNT_ID` and `REGION` constants in `%ROOT_DIR%/config/secret_config.py` file

## Virtualenv

The initialization process requires a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on Windows:

```
$ python -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

## Dependencies

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

## Bootstraping

Deployment requires that containers already exist in the account and region you are deploying into. Creating them is called bootstrapping. To bootstrap, issue:

```
$ cdk bootstrap
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `requirements.txt` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state

## Testing

## API key

Copy generated apiKey from AWS Console. Steps:
 
 * login to `AWS Console`
 * open `Amazon API Gateway` service
 * in `API Keys` tab copy `API key` field 

## Postman collection

 * Edit API key in postman collection `%ROOT_DIR%/announcements.postman_collection.json`
 * Import collection
 * Test API

## Unittests

It is possible to run pytest tests for lambdas ( `%ROOT_DIR%/lambda/test_lambda.py` ): 
```
$ pytest
```

Enjoy!
