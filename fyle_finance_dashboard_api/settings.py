"""
Django settings for fyle_finance_dashboard_api project.

Generated by 'django-admin startproject' using Django 1.11.29.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ha9e6vkv-k770qb-b96w0-j*)q)mv13an4&y=d#85s=i6u(ap%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Installed Apps

    'rest_framework',
    'corsheaders',

    # User Created Apps
    'apps.users',
    'fyle_rest_auth',
    'apps.enterprise',
    'apps.exports'
]

MIDDLEWARE = [
    'request_logging.middleware.LoggingMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsPostCsrfMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'fyle_finance_dashboard_api.urls'
AUTH_USER_MODEL = 'users.User'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

FYLE_REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'apps.users.serializers.UserSerializer'
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        'apps.enterprise.permissions.EnterprisePermissions'
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'fyle_rest_auth.authentication.FyleJWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}

WSGI_APPLICATION = 'fyle_finance_dashboard_api.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

if os.environ.get('DATABASE_URL', ''):
    DATABASES = {
        'default': dj_database_url.config()
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST'),
            'PORT': os.environ.get('DB_PORT'),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

API_URL = os.environ.get('API_URL')
FYLE_TOKEN_URI = os.environ.get('FYLE_TOKEN_URI')
FYLE_CLIENT_ID = os.environ.get('FYLE_CLIENT_ID')
FYLE_CLIENT_SECRET = os.environ.get('FYLE_CLIENT_SECRET')
FYLE_BASE_URL = os.environ.get('FYLE_BASE_URL')
FYLE_JOBS_URL = os.environ.get('FYLE_JOBS_URL')
GSHEET_CREDS = {
  "type": "service_account",
  "project_id": "multi-org-export",
  "private_key_id": "6b3cc401116458996322bca843c33c293bb2f906",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCqxFhq+QCyD02m\nCmNie0sLmbghgcm5t1E4hYA7gJgXf8cgGQ37OtjjY3h79I9hKYZsOtlzGDStyDph\nOjkMPd5HKnGIFrAipfSKgtc9DnPUXVeSBwL7mu/UB20UgwsrRLPSSqP/9cshWuFd\ndFjBkKDNw1OTfA6Uw4MRVE/c29Yil16d03E7BkE23Knk3EeqCo3maweDJOWhWyJN\nX3wrI8ir9IzbiUEtWWgMwEhEPkJWhmCIbtfu7I4bfGuq+xbee4S5qYcfhwiZbHJm\nU3h28blmBMvuDebG1lM3CWbgC7+u49MxhUApj3XoL587LJwuUSEYtOM/N0Fzj/js\nO2EcN2b/AgMBAAECggEAC3/zdsJUAkNQXSK/9KBzulFDLbmtMwnquOqzBJuXvAvJ\nbIDwO+XuBMof3meAX4oWi/CFA+CY05PzUoIQPqHMxHAerljdl0e9XLW/XVSjoKTn\nwjHuSOSMy0BaX5I/mbQjtyd6cEDfyakMGjYJybQKqcpCNS40JF9SOUPudbCCqCUu\ne2DVPDmH0PjIGV6hvjgAjAKfaQek14FVrAqeaqFdEHSfrakgmNCmFlIsIznmOgYU\nKFcXrc753zFhHtjsTwiqAkdtUAEBz4Xs0chw+O4s4c3ZhtVYU7D2mzfI/t0guF8P\nD84JUth/9ryO1nGtOzFrQC75GEc6gWuKXTgZd4mKcQKBgQDR0bPrPxUBVKV0kuLg\nkKpB7ryaOgM1ALsQi4nV82QE4GTHpJmgd/VOy2Icy+47f9kEFGz7g91U8y2dUn2Y\niM5XdNt3m+5YHei66CtliAUvlJUF1BVtLuXTgC99cG0snfeeZjV688M6kKrK4ox7\ni6o4SP6rb+uV6O7HGr56JDGTVwKBgQDQWj2glPw1y+I/8xfoK1Z2CDnnqXOrmHWi\nVKPvfK7+76W2NaXjZQcrH2h9x4W2lkwEmPEqf7e8N1QFGdqMRR+VcBAm9Tu0zVcg\nL5RHhb2NrrUDR81YOhH8Q5hvUhloOrX4L8tHcz9BaDegR9gBWtykku6+y+CyqWeP\nxAzavT1omQKBgDAp9ycVP/kiOSjdXv81th+Uce7lSj8sf8R4g5d9W4RTDk9V1X4k\ni0cfINKDbZhy7JonJi1GQ9RwThRDD1mobdVdmdOHE9teYkIlcXDJHIejj+HaoWCC\n13cJgd1FpYoMaP8Pb09eDX6wHsSb5Kunj9eDyhIIiwfKhKVn2jmnfUnZAoGAG7qG\nzSJG1poFyGD/44QxA5BgtHYW0NV/glUlZDAB0ifus+s74qGFbLXHYEX3g69I+quo\nHPHWcBQk+HDSZyyj4W2CmMy2X3+cgsoSP9qKuZpwuLkLmRxRXHNajCYu/3Ig2aDy\nutWZq4jFLm2hT7zZ9IUhhP75Lo3hHH8I/uuEirECgYEArR4CdbMQ/o/VbORnqdAQ\nW9SWmhWDj9PqHnT58guD0V9p71BAypiGcjLx56DhtoVJw+V5qgrx/lcxT9Ar0atN\nqtkRaDx/Ul5QSwebZis/DGN15Xk84bydleICzN5QXO1mXgpgzk4CazEYAhkcAvQY\nvE1PCJVrPqLxTfk2vibBjWs=\n-----END PRIVATE KEY-----\n",
  "client_email": "multiorgexport@multi-org-export.iam.gserviceaccount.com",
  "client_id": "104273631591313885223",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/multiorgexport%40multi-org-export.iam.gserviceaccount.com"
}
CORS_ORIGIN_ALLOW_ALL = True