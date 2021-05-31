import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="microservice",
    version="0.0.1",

    description="CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="DimaAntoniuk",

    package_dir={"": "microservice"},
    packages=setuptools.find_packages(where="microservice"),

    install_requires=[
        "aws-cdk.core==1.106.1",
        "aws-cdk.aws_lambda==1.106.1",
        "aws-cdk.aws_dynamodb==1.106.1",
        "aws-cdk.aws_events==1.106.1",
        "aws-cdk.aws_events_targets==1.106.1",
        "aws-cdk.aws_apigateway==1.106.1"
    ],

    python_requires=">=3.8",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
