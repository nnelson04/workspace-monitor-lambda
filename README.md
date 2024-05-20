# Workspace Monitor Lambda

### Workspace Monitor Lambda is an AWS Lambda-based project designed to automate the monitoring, maintenance, and tagging of AWS WorkSpaces. It includes two main Lambda functions:

Workspace Monitor Function: Monitors workspace activity, sends notifications to users based on their last known connection, and terminates inactive workspaces after a specified period.
Tag Workspace Function: Tags AWS WorkSpaces with the creation date when they are created.
Features
Automated Monitoring: Periodically checks the last known user connection timestamp for each AWS Workspace.
Configurable Notifications: Sends email alerts to users at predefined intervals (e.g., 85 days, 90 days) using Amazon SES.
Automatic Cleanup: Terminates workspaces that have not been used for a specified number of days.
Tagging on Creation: Tags new AWS WorkSpaces with the creation date.
Customizable Settings: All company-specific values and time intervals are configurable via environment variables.
AWS CDK Deployment: Easily deploy the Lambda functions and associated resources using AWS Cloud Development Kit (CDK).
## Getting Started
### Prerequisites
AWS CLI configured with appropriate permissions
Node.js and npm installed
Python 3.8 or later
AWS CDK installed (npm install -g aws-cdk)
## Installation
### Clone the repository:

 ```
 git clone https://github.com/your-username/workspace-monitor-lambda.git
 cd workspace-monitor-lambda
 ```
### Install dependencies:

 ```
 pip install -r requirements.txt
 ```
### Project Structure
```
workspace-monitor/
├── lambda/
│   ├── tag_workspace_on_create.py
│   └── workspace_monitor.py
├── workspace_monitor/
│   └── workspace_monitor_stack.py
├── app.py
├── cdk.json
└── requirements.txt
```
## Configuration
The Lambda functions use the following environment variables for configuration:

WARN_DAYS: Number of days after which a warning email is sent (default: 85).
CUTOFF_DAYS: Number of days after which the workspace is terminated (default: 90).
TWO_WEEKS_DAYS: Number of days after creation after which an unused workspace is terminated (default: 14).
DOMAIN_NAME: Domain name used to construct user email addresses (e.g., example.com).
SES_SOURCE_EMAIL: Source email address for sending notifications.
SES_ADMIN_EMAIL: Admin email address to receive copies of notifications.
## Deployment
### Synthesize the AWS CloudFormation templates:

 ```
 cdk synth
 ```
### Deploy the stack:

 ```
 cdk deploy
 ```
## Lambda Functions
### Workspace Monitor Function
File: lambda/workspace_monitor.py
Description: Monitors AWS WorkSpaces, sends notifications, and deletes inactive workspaces.
Environment Variables:
WARN_DAYS
CUTOFF_DAYS
TWO_WEEKS_DAYS
DOMAIN_NAME
SES_SOURCE_EMAIL
SES_ADMIN_EMAIL
Tag Workspace Function
File: lambda/tag_workspace_on_create.py
Description: Tags AWS WorkSpaces with the creation date when they are created.
Triggers: CloudWatch Events rule for WorkSpaces creation events.

## License
This project is licensed under the Apache License - see the LICENSE file for details.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request.
