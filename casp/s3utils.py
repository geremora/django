from django.conf import settings
from storages.backends.s3boto import S3BotoStorage

StaticRootS3BotoStorage = lambda: S3BotoStorage(bucket=settings.AWS_STATIC_BUCKET_NAME)
MediaRootS3BotoStorage = lambda: S3BotoStorage(acl='private',
                                               bucket=settings.AWS_MEDIA_BUCKET_NAME)
