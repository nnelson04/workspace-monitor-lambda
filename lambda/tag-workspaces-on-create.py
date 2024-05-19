import json
import boto3
from datetime import datetime

def lambda_handler(event, context):
    # Initialize the boto3 client for WorkSpaces
    workspaces_client = boto3.client('workspaces')
    
    # Extract the WorkSpace ID from the event
    workspace_id = event['detail']['responseElements']['workspaceId']
    
    # Get the current date in YYYY-MM-DD format
    created_date = datetime.utcnow().strftime('%Y-%m-%d')
    
    # Tag the WorkSpace with the "CreatedDate" tag
    response = workspaces_client.create_tags(
        ResourceId=workspace_id,
        Tags=[
            {
                'Key': 'CreatedDate',
                'Value': created_date
            },
        ]
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('WorkSpace tagged successfully')
    }
