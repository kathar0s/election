# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'survey', views.SurveyViewSet)
router.register(r'agency', views.AgencyViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
