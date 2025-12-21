from django.test import TestCase, override_settings
from django.urls import reverse

from tests.testapp.models import Person


class TestGlobalSearchIntegration(TestCase):
    def setUp(self):
        self.user = self._create_superuser()
        self.client.force_login(self.user)

    def _create_superuser(self):
        from django.contrib.auth import get_user_model

        return get_user_model().objects.create_superuser(
            username="admin", email="admin@example.com", password="pass"
        )

    def test_search_returns_results_for_superuser(self):
        person = Person.objects.create(name="John Lennon", bio="The Beatles")

        response = self.client.get(reverse("admin_global_search"), {"q": "john"})

        self.assertEqual(response.status_code, 200)
        results = response.context["results"]
        self.assertIn("testapp:person", results)
        self.assertEqual(results["testapp:person"][0]["object_id"], person.pk)
        self.assertEqual(
            results["testapp:person"][0]["admin_url"],
            reverse("admin:testapp_person_change", args=(person.pk,)),
        )

    @override_settings(ADMIN_GLOBAL_SEARCH_RESULT_LIMIT=1)
    def test_search_respects_result_limit_setting(self):
        Person.objects.create(name="Jane One", bio="bio")
        Person.objects.create(name="Jane Two", bio="bio")

        response = self.client.get(reverse("admin_global_search"), {"q": "Jane"})

        results = response.context["results"]["testapp:person"]
        self.assertEqual(len(results), 1)

    def test_whitespace_query_returns_empty_results(self):
        Person.objects.create(name="Some Name", bio="Something")

        response = self.client.get(reverse("admin_global_search"), {"q": "   "})

        self.assertEqual(response.context["results"], {})
