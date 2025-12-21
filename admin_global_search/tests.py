"""Unit tests for the GlobalSearchView helpers."""
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import django
from django.conf import settings
from django.db.models import Q
from django.test import RequestFactory, SimpleTestCase

if not settings.configured:
    settings.configure(
        SECRET_KEY="test-key",
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
        ],
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
        MIDDLEWARE=[],
        ROOT_URLCONF=__name__,
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [],
                "APP_DIRS": True,
                "OPTIONS": {},
            }
        ],
        USE_TZ=True,
    )
django.setup()

urlpatterns = []

from admin_global_search.views import GlobalSearchView  # noqa: E402  pylint: disable=C0413


class TestGlobalSearchView(SimpleTestCase):
    """Covers helper methods on the global search view."""

    def setUp(self):
        self.view = GlobalSearchView()
        self.factory = RequestFactory()

    def test_build_search_query_aggregates_fields_with_or_connector(self):
        q_objects = self.view.build_search_query(["name", "description"], "Beatles")

        self.assertEqual(q_objects.connector, Q.OR)
        self.assertEqual(
            q_objects.children,
            [("name__icontains", "Beatles"), ("description__icontains", "Beatles")],
        )

    def test_user_has_permission_checks_view_permission_for_model(self):
        user = SimpleNamespace(has_perm=MagicMock(return_value=True))
        self.view.request = SimpleNamespace(user=user)
        model = SimpleNamespace(app_label="music", model="artist")

        has_perm = self.view.user_has_permission(model)

        user.has_perm.assert_called_once_with("music.view_artist")
        self.assertTrue(has_perm)

    def test_process_model_returns_none_without_permission(self):
        self.view.user_has_permission = MagicMock(return_value=False)
        model = SimpleNamespace()

        result = self.view.process_model_for_search_results(model, "query")

        self.view.user_has_permission.assert_called_once_with(model)
        self.assertIsNone(result)

    def test_process_model_returns_none_when_no_results(self):
        class DummyModel:
            global_search_fields = ("title",)

        model = SimpleNamespace(
            app_label="library",
            model="book",
            model_class=lambda: DummyModel,
        )
        self.view.user_has_permission = MagicMock(return_value=True)
        self.view.build_search_query = MagicMock(return_value="q-object")
        empty_results = MagicMock()
        empty_results.exists.return_value = False
        self.view.fetch_model_results = MagicMock(return_value=empty_results)

        result = self.view.process_model_for_search_results(model, "gatsby")

        self.view.build_search_query.assert_called_once_with(
            DummyModel.global_search_fields, "gatsby"
        )
        self.view.fetch_model_results.assert_called_once_with(DummyModel, "q-object")
        self.assertIsNone(result)

    def test_process_model_returns_formatted_results_when_available(self):
        class DummyModel:
            global_search_fields = ("title",)

        model = SimpleNamespace(
            app_label="library",
            model="book",
            model_class=lambda: DummyModel,
        )
        self.view.user_has_permission = MagicMock(return_value=True)
        self.view.build_search_query = MagicMock(return_value="q-object")
        non_empty_results = MagicMock()
        non_empty_results.exists.return_value = True
        self.view.fetch_model_results = MagicMock(return_value=non_empty_results)
        self.view.format_results = MagicMock(return_value=("library:book", ["result"]))

        result = self.view.process_model_for_search_results(model, "gatsby")

        self.view.format_results.assert_called_once_with(model, non_empty_results)
        self.assertEqual(result, ("library:book", ["result"]))

    @patch("admin_global_search.views.reverse", return_value="/admin/blog/post/7/change/")
    def test_format_results_returns_admin_linked_payload(self, reverse_mock):
        model = SimpleNamespace(app_label="blog", model="post")

        class DummyObject:
            def __init__(self, pk, label):
                self.pk = pk
                self.label = label

            def __str__(self):
                return self.label

        key, results = self.view.format_results(model, [DummyObject(7, "First post")])

        reverse_mock.assert_called_once_with("admin:blog_post_change", args=(7,))
        self.assertEqual(key, "blog:post")
        self.assertEqual(
            results,
            [
                {
                    "model": "post",
                    "app_label": "blog",
                    "object_id": 7,
                    "str": "First post",
                    "admin_url": "/admin/blog/post/7/change/",
                }
            ],
        )

    @patch("admin_global_search.views.render")
    def test_get_returns_empty_response_when_no_query(self, render_mock):
        request = self.factory.get("/search")
        self.view.request = request

        response = self.view.get(request)

        render_mock.assert_called_once_with(
            request,
            "admin_global_search/results.html",
            {"query": "", "results": {}},
        )
        self.assertEqual(response, render_mock.return_value)

    @patch("admin_global_search.views.render")
    def test_get_collects_results_from_models(self, render_mock):
        request = self.factory.get("/search", {"q": "john"})
        self.view.request = request
        self.view.get_content_types_with_search_fields = MagicMock(
            return_value=["model_a", "model_b"]
        )
        self.view.process_model_for_search_results = MagicMock(
            side_effect=[("app:modela", [{"name": "John"}]), None]
        )

        response = self.view.get(request)

        render_mock.assert_called_once()
        _, template_name, context = render_mock.call_args[0]
        self.assertEqual(template_name, "admin_global_search/results.html")
        self.assertEqual(
            context,
            {"query": "john", "results": {"app:modela": [{"name": "John"}]}},
        )
        self.assertEqual(response, render_mock.return_value)
