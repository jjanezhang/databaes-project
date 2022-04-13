import boto3
from flask import current_app

def s3_client():
    """
        Function: get s3 client
         Purpose: get s3 client
        :returns: s3
    """
    session = boto3.session.Session()
    client = session.client(
        's3',
        aws_access_key_id=current_app.config["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=current_app.config["AWS_SECRET_ACCESS_KEY"]
    )
    return client


def s3_upload_small_files(inp_file_name, s3_bucket_name,
                          inp_file_key, content_type):
    client = s3_client()
    upload_file_response = client.put_object(Body=inp_file_name,
                                             Bucket=s3_bucket_name,
                                             Key=inp_file_key,
                                             ContentType=content_type)
    return upload_file_response

