from django.contrib import admin

from .models import Candidate, Agency, Survey, Rating, Office
from reversion.admin import VersionAdmin


class CandidateAdmin(VersionAdmin):
    list_display = ('number', 'name', 'party', 'is_active')
    search_fields = ['name', ]
    ordering = ('-is_active', 'number', 'name')

admin.site.register(Candidate, CandidateAdmin)


class AgencyAdmin(VersionAdmin):
    list_display = ('name', 'aliases')
    search_fields = ['name', 'aliases']
    ordering = ('name', )

admin.site.register(Agency, AgencyAdmin)


class OfficeAdmin(VersionAdmin):
    list_display = ('name', 'alias')
    search_fields = ['name', 'alias']
    ordering = ('name', )

admin.site.register(Office, OfficeAdmin)


class SurveyAdmin(VersionAdmin):
    list_display = ('name', 'description', 'published', 'is_virtual')
    search_fields = ['name', 'description']
    ordering = ('-published', 'agency')

admin.site.register(Survey, SurveyAdmin)


class RatingAdmin(VersionAdmin):
    list_display = ('survey', 'type', 'target', 'candidate', 'rate')
    search_fields = ['survey__name', 'type', 'target']
    list_filter = ['type', 'target', 'candidate', 'survey__agency']
    ordering = ('survey__published', 'candidate')

admin.site.register(Rating, RatingAdmin)
