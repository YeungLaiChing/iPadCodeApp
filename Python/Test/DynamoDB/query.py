import boto3 
from boto3.dynamodb.conditions import Key 

def query_book(book_id, dynamodb=None):
    dynamodb = boto3.resource( 'dynamodb', endpoint_url="http://192.168.0.3:8000",region_name='us-east-1',aws_access_key_id='key',
         aws_secret_access_key= '')
    books_table = dynamodb.Table('Books')

    response = books_table.query(
        KeyConditionExpression=Key('book_id').eq(1001)
    )
    return response['Items']

if __name__ == '__main__':
    query_id = 10001
    print(f"Book ID: {query_id}")
    books_data = query_book(query_id)
    for book_data in books_data:
       print(book_data['book_id'], ":", book_data['title'])