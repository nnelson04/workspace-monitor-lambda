from aws_cdk import core
from workspace_monitor.workspace_monitor_stack import WorkspaceMonitorStack

app = core.App()
WorkspaceMonitorStack(app, "WorkspaceMonitorStack")
app.synth()