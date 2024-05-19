import boto3
from datetime import datetime, timedelta, timezone
import time
from botocore.exceptions import ClientError
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    ses_client = boto3.client('ses')
    workspaces_client = boto3.client('workspaces')
    warn_days = int(os.getenv('WARN_DAYS', 85))
    cutoff_days = int(os.getenv('CUTOFF_DAYS', 90))
    two_weeks_days = int(os.getenv('TWO_WEEKS_DAYS', 14))
    domain_name = os.getenv('DOMAIN_NAME', 'example.com')
    ses_source_email = os.getenv('SES_SOURCE_EMAIL', 'no-reply@example.com')
    ses_admin_email = os.getenv('SES_ADMIN_EMAIL', 'admin@example.com')

    warn_date = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(days=warn_days)
    cutoff_date = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(days=cutoff_days)
    two_weeks_ago = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(days=two_weeks_days)

    paginator = workspaces_client.get_paginator('describe_workspaces')
    for page in paginator.paginate():
        workspace_ids = [workspace['WorkspaceId'] for workspace in page['Workspaces']]
        if workspace_ids:
            connection_statuses = workspaces_client.describe_workspaces_connection_status(WorkspaceIds=workspace_ids)
            for status in connection_statuses['WorkspacesConnectionStatus']:
                last_known_user_connection = status.get('LastKnownUserConnectionTimestamp', 'Not Set')
                workspace_id = status['WorkspaceId']
                workspace_details = describe_workspaces_with_backoff(workspaces_client, [workspace_id])
                if workspace_details['Workspaces']:
                    workspace_info = workspace_details['Workspaces'][0]
                    username = workspace_info.get('UserName', 'Unknown')
                    email_address = f"{username}@{domain_name}" if username != 'Unknown' else f'noreply@{domain_name}'
                    workspace_info['Email'] = email_address
                    if last_known_user_connection == 'Not Set':
                        logger.info('Not Used')
                        creation_date = get_creation_date(workspaces_client, workspace_id)
                        if creation_date:
                            creation_date = datetime.strptime(creation_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                            if creation_date < two_weeks_ago:
                                delete_workspace(workspaces_client, workspace_id)
                                send_email(ses_client, email_address, workspace_info, two_weeks_days, ses_source_email, ses_admin_email)
                    else:
                        if last_known_user_connection.date() == warn_date.date():
                            send_email(ses_client, email_address, workspace_info, warn_days, ses_source_email, ses_admin_email)
                        elif last_known_user_connection < cutoff_date:
                            delete_workspace(workspaces_client, workspace_id)
                            send_email(ses_client, email_address, workspace_info, cutoff_days, ses_source_email, ses_admin_email)

def describe_workspaces_with_backoff(workspaces_client, workspace_ids):
    retries = 0
    max_retries = 5
    wait_time = 1

    while retries < max_retries:
        try:
            return workspaces_client.describe_workspaces(WorkspaceIds=workspace_ids)
        except ClientError as e:
            if e.response['Error']['Code'] == 'ThrottlingException':
                time.sleep(wait_time)
                wait_time *= 2
                retries += 1
            else:
                raise e
    raise Exception("Reached maximum retries for AWS API call")

def get_creation_date(workspaces_client, workspace_id):
    try:
        response = workspaces_client.describe_tags(ResourceId=workspace_id)
        for tag in response['TagList']:
            if tag['Key'] == 'Creation Date':
                return tag['Value']
    except ClientError as e:
        logger.error(f"Failed to get tags for workspace {workspace_id}: {e}")
    return None

def send_email(ses_client, email_address, workspace_info, days, ses_source_email, ses_admin_email):
    workspace_details_html = create_workspace_details_html(workspace_info)
    if days == 14:
        message = f"Hello, your ITVM has not been used for 2 weeks since its creation and has been deleted. Please contact the Workspaces Team if you need a new Workspace.<br><br>{workspace_details_html}"
    elif days == 85:
        message = f"Hello, your workspace has not been logged into for 85 days. In 5 days, your Workspace will be deleted and will be irrecoverable. Please contact support if you plan to actively use this machine.<br><br>{workspace_details_html}"
    elif days == 90:
        message = f"Hello, your workspace has not been used for 90 days and has been deleted. Please submit a ticket or contact the Workspaces Team if you need a new Workspace.<br><br>{workspace_details_html}"

    ses_client.send_email(
        Source=ses_source_email,
        Destination={
            'ToAddresses': [email_address, ses_admin_email]
        },
        Message={
            'Subject': {'Data': 'Workspace Notification'},
            'Body': {'Html': {'Data': message}}
        }
    )

def delete_workspace(workspaces_client, workspace_id):
    try:
        workspaces_client.terminate_workspaces(
            TerminateWorkspaceRequests=[{'WorkspaceId': workspace_id}]
        )
        logger.info(f"Deleted workspace: {workspace_id}")
    except ClientError as e:
        logger.error(f"Failed to delete workspace {workspace_id}: {e}")

def create_workspace_details_html(workspace_info):
    return f"""
    <table>
        <tr><th>Workspace ID</th><td>{workspace_info['WorkspaceId']}</td></tr>
        <tr><th>Workspace Machine Name</th><td>{workspace_info['ComputerName']}</td></tr>
        <tr><th>User Name</th><td>{workspace_info.get('UserName', 'Unknown')}</td></tr>
        <tr><th>Email</th><td>{workspace_info['Email']}</td></tr>
        <tr><th>Last Connection</th><td>{workspace_info.get('LastKnownUserConnectionTimestamp', 'Never')}</td></tr>
    </table>
    """
