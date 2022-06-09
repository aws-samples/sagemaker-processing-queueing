import boto3
import json
import uuid

if __name__ == '__main__':
    client = boto3.client('sqs')
    account_id = boto3.client('sts').get_caller_identity()['Account']
    for i in range(10):
        send_message_resp = client.send_message(
            QueueUrl=f'https://sqs.us-east-1.amazonaws.com/{account_id}/SageMakerJobs.fifo',
            MessageBody=json.dumps({
                "ProcessingJobName": f"{uuid.uuid4()}",
                "RoleArn": f"arn:aws:iam::{account_id}:role/SageMakerExecutionRole",
                "AppSpecification": {
                    "ImageUri": "737474898029.dkr.ecr.us-east-1.amazonaws.com/sagemaker-scikit-learn:0.20.0-cpu-py3"
                },
                "ProcessingResources": {
                    "ClusterConfig": {
                        "InstanceCount": 1,
                        "InstanceType": "ml.t3.medium",
                        "VolumeSizeInGB": 10
                    }
                }
            }),
            MessageDeduplicationId=f'{uuid.uuid4()}',
            MessageGroupId='1'
        )
        print(send_message_resp)
