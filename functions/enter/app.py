import os
from typing import Dict

import boto3
import json
import uuid
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
step_functions = boto3.client('stepfunctions')


def lambda_handler(event, context) -> Dict:
    print(json.dumps(event))

    table_name = os.getenv('TABLE_NAME')
    state_machine_arn = os.getenv('STATE_MACHINE_ARN')

    failed_messages = []
    for record in event['Records']:
        job_specs = json.loads(record['body'])
        try:
            update_item_resp = dynamodb.Table(table_name).update_item(
                Key={
                    'InstanceType': job_specs['ProcessingResources']['ClusterConfig']['InstanceType']
                },
                UpdateExpression='SET RunningInstancesCount = RunningInstancesCount + :count',
                ExpressionAttributeValues={
                    ':count': 1
                },
                ConditionExpression='RunningInstancesCount < RunningInstancesLimit'
            )
            start_execution_resp = step_functions.start_execution(
                stateMachineArn=state_machine_arn,
                name=f'{uuid.uuid4()}',
                input=record['body']
            )
        except ClientError as err:
            if err.response['Error']['Code'] == 'ConditionalCheckFailedException':
                failed_messages.append(record['messageId'])
            else:
                raise
    print(failed_messages)
    return {'batchItemFailures': [{'itemIdentifier': m} for m in failed_messages]}

