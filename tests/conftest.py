from django.conf import settings
from django.test.utils import setup_databases, setup_test_environment, teardown_databases, teardown_test_environment

_db_config = None


def pytest_configure():
    if settings.configured:
        return

    settings.configure(
        SECRET_KEY="test-key",
        INSTALLED_APPS=[
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "admin_global_search",
            "tests.testapp",
        ],
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
        MIDDLEWARE=[
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
        ],
        ROOT_URLCONF="tests.urls",
        MIGRATION_MODULES={"tests.testapp": None},
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [],
                "APP_DIRS": True,
                "OPTIONS": {},
            }
        ],
        PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
        USE_TZ=True,
        DEFAULT_AUTO_FIELD="django.db.models.AutoField",
    )

    import django  # pylint: disable=import-outside-toplevel

    django.setup()

    setup_test_environment()

    global _db_config  # pylint: disable=global-statement
    _db_config = setup_databases(verbosity=0, interactive=False)


def pytest_unconfigure():
    if not settings.configured:
        return
    if _db_config is not None:
        teardown_databases(_db_config, verbosity=0)
    teardown_test_environment()
