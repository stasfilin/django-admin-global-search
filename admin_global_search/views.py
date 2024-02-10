from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse
from django.views import View


class GlobalSearchView(LoginRequiredMixin, View):
    def get_query(self):
        return self.request.GET.get("q", "")

    def get_content_types_with_search_fields(self):
        return ContentType.objects.filter(
            id__in=[
                ct.id
                for ct in ContentType.objects.all()
                if hasattr(ct.model_class(), "global_search_fields")
                and ct.model_class() is not None
            ]
        )

    def user_has_permission(self, model):
        perm = f"{model.app_label}.view_{model.model}"
        return self.request.user.has_perm(perm)

    def build_search_query(self, search_fields, query):
        q_objects = Q()
        for field in search_fields:
            q_objects |= Q(**{f"{field}__icontains": query})
        return q_objects

    def fetch_model_results(self, model_class, q_objects):
        return model_class.objects.filter(q_objects)

    def format_results(self, model, model_results):
        model_key = f"{model.app_label}:{model.model}"
        formatted_results = []
        for result in model_results:
            admin_url = reverse(
                f"admin:{model.app_label}_{model.model}_change",
                args=(result.pk,),
            )
            formatted_results.append(
                {
                    "model": model.model,
                    "app_label": model.app_label,
                    "object_id": result.pk,
                    "str": str(result),
                    "admin_url": admin_url,
                }
            )
        return model_key, formatted_results

    def process_model_for_search_results(self, model, query):
        if not self.user_has_permission(model):
            return None
        model_class = model.model_class()
        q_objects = self.build_search_query(model_class.global_search_fields, query)
        model_results = self.fetch_model_results(model_class, q_objects)
        if model_results.exists():
            return self.format_results(model, model_results)
        return None

    def get(self, request, *args, **kwargs):
        query = self.get_query()
        if not query:
            return render(
                request,
                "admin_global_search/results.html",
                {"query": "", "results": {}},
            )

        results = {}
        content_types = self.get_content_types_with_search_fields()
        for model in content_types:
            search_result = self.process_model_for_search_results(model, query)
            if search_result:
                model_key, formatted_results = search_result
                results.setdefault(model_key, []).extend(formatted_results)

        return render(
            request,
            "admin_global_search/results.html",
            {"query": query, "results": results},
        )
