# donation_platform/settings.py
# donation_platform/donation_platform/settings.py
import os
from pathlib import Path
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'default-development-secret-key-if-not-set') # Replace with your actual development key if desired
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
BASE_DIR = Path(__file__).resolve().parent.parent
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',  # Your app
]

# ... other settings
# donation_platform/settings.py
# ...
AUTH_USER_MODEL = 'core.CustomUser'
# ...


# donation_platform/donation_platform/settings.py

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [], # You can add 'DIRS': [os.path.join(BASE_DIR, 'templates')] if you have global templates
        'APP_DIRS': True, # This is crucial for Django to find templates within your app directories (e.g., core/templates/core/)
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

# donation_platform/donation_platform/settings.py
# WhiteNoise configuration
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', # Essential for sessions (login/logout)
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Essential for user authentication
    'django.contrib.messages.middleware.MessageMiddleware', # Essential for Django's message framework
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
     'whitenoise.middleware.WhiteNoiseMiddleware',
]

# donation_platform/donation_platform/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core', # Your app
    'organization_auth',
    'organization_dashboard',
]

# donation_platform/donation_platform/settings.py

DEBUG = True # Keep this True for development for now

ALLOWED_HOSTS = [
    '127.0.0.1', # For local development
    'localhost', # For local development
    '.onrender.com',
]


# donation_platform/donation_platform/settings.py

# ... other settings ...

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Optional: STATICFILES_DIRS
# This tells Django where to look for static files in addition to
# the 'static/' folder inside each app.
# Useful for project-wide static files (e.g., a global CSS file or favicon).
import os
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static_project'), # Example: a 'static_project' folder at your project root
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# donation_platform/donation_platform/settings.py

# ... other settings ...

ROOT_URLCONF = 'donation_platform.urls' # This is usually the correct path
# Optional: STATIC_ROOT
# This is where Django will collect all static files for deployment (using collectstatic).
# It should be a directory that your web server can serve directly.
# DON'T use this for development server as it will conflict with STATICFILES_DIRS.
# Uncomment and configure when deploying to production.
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# donation_platform/donation_platform/settings.py

# ... other settings ...

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'your-super-secret-and-random-key-here-do-not-share-this!'

# ... rest of your settings ...

# donation_platform/donation_platform/settings.py

# ... other settings ...

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3', # This will create a db.sqlite3 file in your project root
    }
}
# Render-এ DATABASE_URL এনভায়রনমেন্ট ভেরিয়েবল সেট করা হবে
if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        ssl_require=True
    )
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Custom User Model (ensure this is present and correct)
AUTH_USER_MODEL = 'core.CustomUser'
# Login/Logout redirects (adjust as needed)
LOGIN_URL = 'organization_auth:login' # Where users are redirected if not logged in
LOGIN_REDIRECT_URL = 'organization_dashboard:dashboard' # Where users go after successful login
LOGOUT_REDIRECT_URL = '/' # Where users go after logout

# ... rest of your settings ...