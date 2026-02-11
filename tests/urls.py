from django.contrib import admin
from django.urls import path

from admin_global_search.views import GlobalSearchView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("search/", GlobalSearchView.as_view(), name="admin_global_search"),
]
