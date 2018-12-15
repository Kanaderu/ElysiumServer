from .base import *

print('Running In Production Mode')

DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')
ALLOWED_HOSTS = ['*']

try:
    from .local import *
except ImportError:
    pass
