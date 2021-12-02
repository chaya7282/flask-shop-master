import boto3
from botocore.client import Config
from flask import session, current_app

def _get_s3_resource():
    if current_app.config["S3_KEY"] and current_app.config["S3_SECRET"]:
        return boto3.resource(
            's3',
            aws_access_key_id=current_app.config["S3_KEY"],
            aws_secret_access_key=current_app.config["S3_SECRET"]
        )
    else:
        return boto3.resource('s3')


def get_bucket():
    s3_resource = _get_s3_resource()
    if 'bucket' in session:
        bucket = session['bucket']
    else:
        bucket = current_app.config["S3_BUCKET"]

    return s3_resource.Bucket(bucket)


def get_presigned_url(filename):

    s3_client = boto3.client("s3", aws_access_key_id=current_app.config["S3_KEY"],
                             aws_secret_access_key=current_app.config["S3_SECRET"], region_name = current_app.config["AWS_S3_REGION_NAME"], config=Config(signature_version='s3v4'))


    presigned_url = s3_client.generate_presigned_url('get_object', Params = {'Bucket':
    current_app.config["S3_BUCKET"], 'Key': filename}, ExpiresIn = 3600)

    return presigned_url


def get_buckets_list():
    client = boto3.client('s3')
    return client.list_buckets().get('Buckets')

def get_buckets_list():
    client = boto3.client('s3')

