# Django Admin Global Search
[![Downloads](https://static.pepy.tech/badge/django-admin-global-search)](https://pepy.tech/project/django-admin-global-search)
[![Downloads](https://static.pepy.tech/badge/django-admin-global-search/month)](https://pepy.tech/project/django-admin-global-search)
[![Downloads](https://static.pepy.tech/badge/django-admin-global-search/week)](https://pepy.tech/project/django-admin-global-search)

## Introduction
This Django application introduces a GlobalSearchView, designed to perform a global search across various models within the Django admin site.
![alt text](https://github.com/stasfilin/django-admin-global-search/blob/main/assets/main.png)
![alt text](https://github.com/stasfilin/django-admin-global-search/blob/main/assets/results.png)

## Features
* Global Search: Enables searching across multiple models from a single query.
* Dynamic Model Inclusion: Automatically includes models that define `global_search_fields`, allowing for flexible search configurations.
* Admin Integration: Provides direct links to the admin change page for each search result, facilitating easy editing.

## Getting Started:

### Prerequisites
* Python versions 3.8+.
* Django version 3+

### Installation Steps
Install with command `pip install django-admin-global-search`.

### Usage
To use `django-admin-global-search` in your Django project, you need to update your models and URL configurations.
1. Add `admin_global_search` to your `INSTALLED_APPS` setting before `django.contrib.admin`.
```python
INSTALLED_APPS = [
    "admin_global_search",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    ...
]
```
2. Ensure your models have a `global_search_fields` attribute that specifies the fields to be included in the search. Example:
```python
class Artist(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)

    global_search_fields = ("name", "bio")

    def __str__(self):
        return self.name
```
2. Update your project's urls.py to include the GlobalSearchView. Example:
```python
...
from admin_global_search.views import GlobalSearchView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("search/", GlobalSearchView.as_view(), name="admin_global_search"),
    ...
]
```

## Contributing
Contributions to the project are welcome. To contribute:
1. Fork the repository.
2. Create a new feature branch for your contribution.
3. Commit your changes with a descriptive message.
4. Push your changes to GitHub.
5. Submit a pull request for review.

## License
The project is made available under the **BSD 3-Clause License**. Please refer to the LICENSE file for more details.
