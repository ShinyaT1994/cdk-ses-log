#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk_ses_log.cdk_ses_log_stack import CdkSesLogStack


app = cdk.App()
CdkSesLogStack(app, "CdkSesLogStack",)

app.synth()
