# find the root of this project,
# so we can use relative paths
# for our database and templates
import os
root = os.path.dirname(__file__)


DEBUG = True
TEMPLATE_DEBUG = DEBUG


# send an e-mail notification when any
# exception is raised in production
ADMINS = (
	("Adam Mckaig", "amckaig@unicef.org"),
	("Evan Wheeler", "ewheeler@unicef.org")
)

# database settings
DATABASE_NAME = root + "/dev.sqlite"
DATABASE_ENGINE = "sqlite3"


# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = "Africa/Addis_Ababa"

# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"








SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = "/assets/admin/"

# Make this unique, and don't share it with anybody.
SECRET_KEY = '2=&ac2hj3j+_#dzi4cic#-qk(!+4ux7-c6ht_buy2zw9e%z=vr'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'webui.urls'

TEMPLATE_DIRS = (
    root + "/inventory/templates",
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.sites',
    'django.contrib.admin',
    'webui.inventory',
)

