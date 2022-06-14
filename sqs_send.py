import boto3
import json
import uuid
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', type=int, default=3)
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

    sagemaker_processing_job_role_arn = None
    for output in stack['Outputs']:
        if output['OutputKey'] == 'SageMakerProcessingJobRoleArn':
            sagemaker_processing_job_role_arn = output['OutputValue']
            break

    sqs_client = session.client('sqs')

    queue_url_response = sqs_client.get_queue_url(
        QueueName='SageMakerJobs.fifo'
    )

    get_caller_identity_response = session.client('sts').get_caller_identity()

    account_id = get_caller_identity_response['Account']

    instance_type = 'ml.t3.medium'

    for i in range(args.n):
        send_message_response = sqs_client.send_message(
            QueueUrl=queue_url_response['QueueUrl'],
            MessageBody=json.dumps({
                "ProcessingJobName": f"{uuid.uuid4()}",
                "RoleArn": sagemaker_processing_job_role_arn,
                "AppSpecification": {
                    # Service public image
                    "ImageUri": "683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-scikit-learn:0.20.0-cpu-py3"
                },
                "ProcessingResources": {
                    "ClusterConfig": {
                        "InstanceCount": 1,
                        "InstanceType": instance_type,
                        "VolumeSizeInGB": 10
                    }
                }
            }),
            MessageDeduplicationId=f'{uuid.uuid4()}',
            MessageGroupId=instance_type
        )
        print(send_message_response)
