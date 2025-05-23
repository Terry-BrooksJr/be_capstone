import os
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class StaticStorage(S3Boto3Storage):
    location ="static"
    default_acl = "public-read"
    file_overwrite = True