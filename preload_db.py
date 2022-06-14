import argparse
import boto3

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--region', type=str, default='us-east-1')
    parser.add_argument('--stack-name', dest='stack_name', type=str, required=True)

    args = parser.parse_args()

    session = boto3.Session(region_name=args.region)

    cloud_formation_client = session.client('cloudformation')

    describe_stack_response = cloud_formation_client.describe_stacks(
        StackName=args.stack_name
    )
    stacks = describe_stack_response['Stacks']
    if len(stacks) == 0:
        raise Exception('Please deploy stack as per README.md')
    stack = stacks[0]

    table_name = None
    for output in stack['Outputs']:
        if output['OutputKey'] == 'CounterTableName':
            table_name = output['OutputValue']
            break

    service_quotas_client = session.client('service-quotas')

    dynamo_db = session.resource('dynamodb')

    paginator = service_quotas_client.get_paginator('list_service_quotas')
    response_iterator = paginator.paginate(
        ServiceCode='sagemaker'
    )
    table = dynamo_db.Table(table_name)
    for response in response_iterator:
        for quota in response['Quotas']:
            quota_name = quota['QuotaName']
            if 'for processing job usage' not in quota_name:
                continue
            instance_type, *_ = quota_name.split(' ')
            update_item_resp = table.update_item(
                Key={
                    'InstanceType': instance_type
                },
                UpdateExpression='SET RunningInstancesCount = :count, RunningInstancesLimit = :limit',
                ExpressionAttributeValues={
                    ':count': 0,
                    ':limit': int(quota['Value'])
                },
            )
            print(update_item_resp)
