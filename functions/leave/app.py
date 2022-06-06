import json
import os

import boto3

dynamodb = boto3.resource('dynamodb')


def lambda_handler(event, context) -> None:
    print(json.dumps(event))

    table_name = os.getenv('TABLE_NAME')

    update_item_resp = dynamodb.Table(table_name).update_item(
        Key={
            'InstanceType': event['ProcessingResources']['ClusterConfig']['InstanceType']
        },
        UpdateExpression='SET RunningInstancesCount = RunningInstancesCount - :count',
        ExpressionAttributeValues={
            ':count': 1
        },
    )

    status_code = update_item_resp['ResponseMetadata']['HTTPStatusCode']
    if status_code != 200:
        raise Exception(f'DynamoDB returned status code {status_code}')
