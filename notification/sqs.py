import boto3

#Create an AWS session

session = boto3.Session(
aws_access_key_id='<your_access_key>',
aws_secret_access_key='<your_secret_key>',
region_name='<your_region>'
)

#Get the SQS client

sqs = session.client('sqs')

#Send a message to the queue
response = sqs.send_message(QueueUrl='<your_queue_url>',
                            MessageBody='Hello, World!'
                           )

#Receive messages from the queue
response = sqs.receive_message(QueueUrl='<your_queue_url>',
                               MaxNumberOfMessages=1,
                               WaitTimeSeconds=0
                               )

#Get the message from the response
message = response.get('Messages', [])[0]

#Print the message
print(message.get('Body'))

#Delete the message from the queue
sqs.delete_message(QueueUrl='<your_queue_url>',
                   ReceiptHandle=message.get('ReceiptHandle')
                  )