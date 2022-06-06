import boto3
import json
import uuid

if __name__ == '__main__':
    client = boto3.client('sqs')
    for i in range(10):
        send_message_resp = client.send_message(
            QueueUrl='https://sqs.us-east-1.amazonaws.com/886385276223/SageMakerJobs.fifo',
            MessageBody=json.dumps({
                "ProcessingJobName": f"{uuid.uuid4()}",
                "RoleArn": "arn:aws:iam::886385276223:role/SageMakerExecutionRole",
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
