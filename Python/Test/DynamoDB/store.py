import json 
from decimal import Decimal
import boto3 

def load_data(books, dynamodb=None):
    dynamodb = boto3.resource(
        'dynamodb', endpoint_url="http://192.168.0.3:8000",region_name='us-east-1',aws_access_key_id='key',
         aws_secret_access_key= '')

    books_table = dynamodb.Table('Books')
    for book in books:
        book_id = (book['book_id'])
        title= book['title']

        print("Displaying book data:", book_id, title)
        books_table.put_item(Item=book)

if __name__ == '__main__':

    with open("/Users/yeunglaiching/Workspace/iPadCodeApp/Python/DynamoDB/data.json") as json_file:
        book_list = json.load(json_file, parse_float=Decimal)
    load_data(book_list)