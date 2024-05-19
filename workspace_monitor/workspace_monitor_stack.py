from aws_cdk import (
    aws_lambda as lambda_,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    core,
)
import os

class WorkspaceMonitorStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define the monitoring Lambda function
        monitor_lambda_function = lambda_.Function(
            self, 'WorkspaceMonitorFunction',
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler='workspace_monitor.lambda_handler',
            code=lambda_.Code.from_asset('lambda'),
            environment={
                'WARN_DAYS': '85',
                'CUTOFF_DAYS': '90',
                'TWO_WEEKS_DAYS': '14',
                'DOMAIN_NAME': 'example.com',
                'SES_SOURCE_EMAIL': 'no-reply@example.com',
                'SES_ADMIN_EMAIL': 'admin@example.com',
            }
        )

        # Grant necessary permissions to the monitoring Lambda function
        monitor_lambda_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    'workspaces:DescribeWorkspaces',
                    'workspaces:DescribeWorkspacesConnectionStatus',
                    'workspaces:DescribeTags',
                    'workspaces:TerminateWorkspaces',
                    'ses:SendEmail',
                    'ses:SendRawEmail',
                    'sts:AssumeRole'
                ],
                resources=['*']
            )
        )

        # Define a rule to trigger the monitoring Lambda function periodically
        monitor_rule = events.Rule(
            self, 'MonitorRule',
            schedule=events.Schedule.rate(core.Duration.days(1)),
        )
        monitor_rule.add_target(targets.LambdaFunction(monitor_lambda_function))

        # Define the tagging Lambda function
        tag_lambda_function = lambda_.Function(
            self, 'TagWorkspaceFunction',
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler='tag_workspace_on_create.lambda_handler',
            code=lambda_.Code.from_asset('lambda')
        )

        # Grant necessary permissions to the tagging Lambda function
        tag_lambda_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    'workspaces:CreateTags',
                ],
                resources=['*']
            )
        )

        # Define a rule to trigger the tagging Lambda function on WorkSpace creation
        tag_rule = events.Rule(
            self, 'TagRule',
            event_pattern={
                "source": ["aws.workspaces"],
                "detail-type": ["AWS API Call via CloudTrail"],
                "detail": {
                    "eventName": ["CreateWorkspaces"]
                }
            }
        )
        tag_rule.add_target(targets.LambdaFunction(tag_lambda_function))

app = core.App()
WorkspaceMonitorStack(app, "WorkspaceMonitorStack")
app.synth()
