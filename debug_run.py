from workflows.workflow import WorkflowOrchestrator

workflow = WorkflowOrchestrator()

result = workflow.run(
    """
    User can login using email and password.
    Forgot password functionality available.
    User should be redirected to dashboard after login.
    """
)

print(result.execution_log)