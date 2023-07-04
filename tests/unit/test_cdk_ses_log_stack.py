import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_ses_log.cdk_ses_log_stack import CdkSesLogStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_ses_log/cdk_ses_log_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkSesLogStack(app, "cdk-ses-log")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
