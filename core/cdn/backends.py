from storages.backends.s3boto3 import S3Boto3Storage


class StaticRootS3Boot3Storages(S3Boto3Storage):
    location = 'static'


class MediaRootS3Boot3Storages(S3Boto3Storage):
    location = 'media'