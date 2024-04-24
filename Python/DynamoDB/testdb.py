
import boto3 as boto3

# Get the service resource.
dynamodb = boto3.resource('dynamodb',endpoint_url='http://192.168.0.9:8000',region_name='us-west-2',aws_access_key_id='DUMMYIDEXAMPLE',
         aws_secret_access_key= 'DUMMYEXAMPLEKEY')


# Create the DynamoDB table.
table = dynamodb.create_table(
    TableName='users3',
    KeySchema=[
        {
            'AttributeName': 'username',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'last_name',
            'KeyType': 'RANGE'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'username',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'last_name',
            'AttributeType': 'S'
        },
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

# Wait until the table exists.
table.wait_until_exists()

# Print out some data about the table.
print(table.item_count)