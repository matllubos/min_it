"""min_it URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import resolvers

from main.admin import admin_site
from main.views import index_view
from copy import copy

# Patching admin URLs
new_patterns = copy(admin_site.urls[0])
for idx, elem in enumerate(new_patterns):
    if isinstance(elem, resolvers.URLResolver):
        if getattr(elem.pattern, '_route') == 'auth/user/':
            setattr(elem.pattern, '_route', 'users/')
        elif getattr(elem.pattern, '_route') == 'main/issue/':
            setattr(elem.pattern, '_route', 'issues/')
            issues_view = elem.url_patterns[0].callback
new_patterns[0].callback = issues_view

urlpatterns = [
    path('', index_view, name='index'),
    path('', (new_patterns, 'admin', 'admin')),
]
