# Description

This projects allows an application to send SageMaker Processing requests to a queue and have concurrency control over how many jobs can run using a particular instance type concurrently as to avoid hitting account quota limits.

This is done by using Amazon DynamoDB as a distributed lock, relying on Amazon DynamoDB's [ConditionalWrite](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/WorkingWithItems.html#WorkingWithItems.ConditionalUpdate)

This technique is explored in depth by the [Controlling concurrency in distributed systems using AWS Step Functions](https://aws.amazon.com/blogs/compute/controlling-concurrency-in-distributed-systems-using-aws-step-functions/).

# Architecture

![architecture](architecture.drawio.png)

# Prerequisites
- AWS Account
- [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) installed

# Deploying

```commandline
sam build 
sam deploy --stack-name <stack-name> --region us-east-1 --resolve-s3 --capabilities CAPABILITY_IAM
```

# Testing

This will populate Amazon DynamoDB with the current account limits and send several job requests to SageMaker. You shouldn't see more than the specified instance limit trying to run concurrently.

```commandline
python preload_db.py --stack-name <stack-name> --region us-east-1
python sqs_send.py --stack-name <stack-name> --region us-east-1 -n 3
```