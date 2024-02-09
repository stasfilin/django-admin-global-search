from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.views import View
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse


class GlobalSearchView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", "")
        results = {}
        if query:
            for model in ContentType.objects.all():
                model_class = model.model_class()
                if model_class is None or not hasattr(model_class, "global_search_fields"):
                    continue
                perm = f"{model.app_label}.view_{model.model}"
                if not request.user.has_perm(perm):
                    continue

                search_fields = model_class.global_search_fields
                q_objects = Q()
                for field in search_fields:
                    q_objects |= Q(**{f"{field}__icontains": query})

                model_results = model_class.objects.filter(q_objects)
                if model_results:
                    model_key = f"{model.app_label}:{model.model}"
                    if model_key not in results:
                        results[model_key] = []

                    for result in model_results:
                        admin_url = reverse(
                            f"admin:{model.app_label}_{model.model}_change",
                            args=(result.pk,),
                        )
                        results[model_key].append(
                            {
                                "model": model.model,
                                "app_label": model.app_label,
                                "object_id": result.pk,
                                "str": str(result),
                                "admin_url": admin_url,
                            }
                        )

        return render(
            request,
            "admin_global_search/results.html",
            {"query": query, "results": results},
        )
