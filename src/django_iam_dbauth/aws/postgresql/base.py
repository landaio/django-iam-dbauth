import getpass

import boto3
from django.db.backends.postgresql import base

from django_iam_dbauth.utils import resolve_cname

from django_iam_dbauth import config


class DatabaseWrapper(base.DatabaseWrapper):
    def get_connection_params(self):
        params = super().get_connection_params()
        enabled = params.pop('use_iam_auth', None)
        if enabled:
            aws_region = params.pop('aws_region', None) or config.DEFAULT_AWS_REGION

            rds_client = boto3.client("rds", region_name=aws_region)

            hostname = params.get('host')

            should_resolve_cname = params.pop('resolve_cname', None) or False
            if should_resolve_cname:
                hostname = resolve_cname(hostname) if hostname else "localhost"

            params["password"] = rds_client.generate_db_auth_token(
                DBHostname=hostname,
                Port=params.get("port", 5432),
                DBUsername=params.get("user") or getpass.getuser(),
            )

        return params
