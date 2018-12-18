from .base import *

print('Running In Production Mode')

DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += [
    'storages',
]

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# AWS S3 Setup
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')

#AWS_QUERYSTRING_AUTH = True
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False
AWS_S3_SECURE_URLS = True
AWS_HEADERS = {
  'Cache-Control': 'max-age=86400',
}

AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
MEDIA_URL = 'https://%s/' % AWS_S3_CUSTOM_DOMAIN

'''
AWS_QUERYSTRING_EXPIRE = 3600
AWS_S3_SIGNATURE_VERSION = 's3v4'
S3_USE_SIGV4 = True
'''

try:
    from .local import *
except ImportError:
    pass
