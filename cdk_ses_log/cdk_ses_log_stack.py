from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_ses as ses,
    aws_iam as iam,
    aws_kinesisfirehose as firehose,
)
from constructs import Construct

class CdkSesLogStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        region = 'ap-northeast-1'
        account_id = '**********'
        
        # SESのメール送信Logを格納するS3 Bucket
        bucket = s3.Bucket(self, 'SesLogsBucket')
        
        # Firehose用のIAM Roleを作成
        firehose_role = iam.Role(
            self,
            'FirehoseDeliveryRole',
            assumed_by=iam.ServicePrincipal("firehose.amazonaws.com")
        )
        firehose_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    's3:PutObject',
                    's3:GetBucketLocation',
                ],
                resources=[
                    bucket.bucket_arn,
                    f'{bucket.bucket_arn}/*'
                ],
            )
        )
        firehose_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    'logs:PutLogEvents',
                ],
                resources=[
                    f'arn:aws:logs:{region}:{account_id}:log-group:/aws/kinesisfirehose/*',
                ],
            )
        )
        
        # Firehose delivery stream
        delivery_stream = firehose.CfnDeliveryStream(
            self,
            'SesLogsDeliveryStream',
            s3_destination_configuration={
                'bucketArn': bucket.bucket_arn,
                'roleArn': firehose_role.role_arn
            }
        )
        
        # SES用のIAM Roleを作成
        ses_role = iam.Role(
            self,
            'SesRole',
            assumed_by=iam.ServicePrincipal("ses.amazonaws.com")
        )
        firehose_statement = iam.PolicyStatement(
            actions=[
                'firehose:PutRecordBatch',
                'firehose:PutRecord',
            ],
            resources=[
                delivery_stream.attr_arn
            ],
        )
        ses_policy = iam.Policy(
            self, 
            'SesPolicy', 
            policy_name='ses-policy',
            statements=[firehose_statement],
        )
        ses_role.attach_inline_policy(ses_policy)
        
        # LogをFirehoseに送るためのConfiguration setを作成する
        configuration_set = ses.CfnConfigurationSet(
            self,
            'SesLoggingConfigurationSet',
            name ='ses-logging',
        )
        event_destination = ses.CfnConfigurationSetEventDestination(
            self,
            'SesLoggingConfigurationSetEventDestination',
            configuration_set_name=configuration_set.name,
            event_destination=ses.CfnConfigurationSetEventDestination.EventDestinationProperty(
                matching_event_types=['send'],
                enabled=True,
                kinesis_firehose_destination=ses.CfnConfigurationSetEventDestination.KinesisFirehoseDestinationProperty(
                    delivery_stream_arn=delivery_stream.attr_arn,
                    iam_role_arn=ses_role.role_arn,
                )
            )
        )
        
        # 依存関係を追加
        configuration_set.add_dependency(delivery_stream)
        event_destination.add_dependency(ses_policy.node.default_child)