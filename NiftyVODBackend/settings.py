import os
from pathlib import Path
import json
from dotenv import load_dotenv
from google.oauth2 import service_account
from google.cloud import storage
from datetime import timedelta

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG') == '1'

ALLOWED_HOSTS = json.loads(os.environ.get('ALLOWED_HOST'))

# Application definition

INSTALLED_APPS = [
    # djangoapps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # my apps
    'rest_framework',

    # OAuth2.0
    'oauth2_provider',

    # my apps
    'api',
    'content',
    'corsheaders',
    'storages',
    'django_filters',
    'payments',
    'parameters',
    'users'
]

LOGIN_URL = '/admin/login/'
AUTH_USER_MODEL = 'users.User'

# Django not to automatically append slashes to api endpoint
APPEND_SLASH = False

CORS_ALLOWED_ORIGINS = [
    'http://localhost:4200',
    'https://api-dot-nwplustv-bbc5a.uc.r.appspot.com',
    # 'http://nwplus.tv',
    'https://nwplus.tv',
    'https://nwplustv-bbc5a.uc.r.appspot.com'
]
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:4200',
    'https://api-dot-nwplustv-bbc5a.uc.r.appspot.com',
    'https://nwplus.tv']

# Allow frontend to get cookies
CORS_ALLOW_CREDENTIALS = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Custom Token Check Middleware
    'auth_server.middleware.CustomTokenCheck',
    # OAuth 2.0
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
]

ROOT_URLCONF = 'NiftyVODBackend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'NiftyVODBackend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases


def getDBHost():
    if DEBUG:
        return os.getenv('DJANGO_DEV_DATABASE_HOST')
    return os.getenv('DJANGO_DATABASE_HOST')


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DJANGO_DATABASE_NAME'),
        'USER': os.getenv('DJANGO_DATABASE_USER'),
        'PASSWORD': os.getenv('DJANGO_DATABASE_PASSWORD'),
        'HOST': getDBHost(),
        'PORT': os.getenv('DJANGO_DATABASE_PORT'),
        'OPTIONS': {'charset': 'utf8mb4'},
    },


}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

# FTP_STORAGE_HOST = 'ftp.nwplus.biz'
# FTP_USER = os.getenv('FTPUser')
# FTP_PASS = os.getenv('FTPPassword')
# FTP_PORT = '21'
# DEFAULT_FILE_STORAGE = 'storages.backends.ftp.FTPStorage'
# FTP_STORAGE_LOCATION = 'ftp://' + FTP_USER + ':' + FTP_PASS + '@194.5.156.102:' + FTP_PORT

DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GOOGLE_APPLICATION_CREDENTIALS = os.path.join(
    BASE_DIR, 'nwplustv-bbc5a-84e0041c7cea.json')
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    os.path.join(BASE_DIR, 'nwplustv-bbc5a-84e0041c7cea.json')
)
UPLOAD_BUCKET = 'api-dot-nwplustv-bbc5a'
UPLOADHLS_BUCKET = 'hls-video-format'

STORAGE_CLIENT = storage.Client(credentials=GS_CREDENTIALS)

PROJECT_ID = os.getenv('PROJECT_ID')
TOPIC_NAME = os.getenv('TOPIC_NAME')

STATIC_URL = '/static/'
# MEDIA_URL = ''

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = 'media_cdn/'
# TEMP = os.path.join(BASE_DIR, 'temp')


# DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


REST_FRAMEWORK = {
    # remove django rest framework ui
    'DEFAULT_RENDERER_CLASSES': (
        # 'rest_framework.renderers.JSONRenderer',
        'NiftyVODBackend.response_formatter.CustomRenderer',
    ),
    # default auth class
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
    ),

    'DEFAULT_PERMISSION_CLASSES': (
        # 'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    # 'EXCEPTION_HANDLER': 'NiftyVODBackend.exception_handler.custom_exception_handler'

}

# Change default user model
AUTH_USER_MOEL = "user.User"

# SECURITY

OAUTH2_PROVIDER = {
    # OpenID Connect
    "OIDC_ENABLED": True,
    "OIDC_RSA_PRIVATE_KEY": os.environ.get("OIDC_RSA_PRIVATE_KEY"),

    # this is the list of available scopes
    'SCOPES': {
        'openid': "OpenID Connect scope",
        'read': 'Read scope',
        'write': 'Write scope',
        'groups': 'Access to your groups',
        'admin': 'Nifty Administartor'
    },

    # extras
    'ALLOWED_REDIRECT_URI_SCHEMES': ["https"]
}
