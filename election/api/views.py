# -*- coding: utf-8 -*-
from collections import defaultdict

from django_pandas.io import read_frame
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import list_route
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from election.models import Survey, Agency, Rating
from election.serializers import SurveySerializer, AgencySerializer


class PaginationClass(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'limit'


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class AgencyViewSet(viewsets.ModelViewSet):
    queryset = Agency.objects.all().order_by('name')
    serializer_class = AgencySerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def perform_create(self, serializer):
        serializer.save()
    

class SurveyViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Survey.objects.all().select_related('agency').prefetch_related('rating_set')
    pagination_class = PaginationClass
    serializers = {
        'default': SurveySerializer,
    }
    ordering_fields = ('id', 'deliver_date')
    ordering = ('-id',)
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    # 트랜드를 알아보기 위해 각각 유형에 대하여 조사기관별 (전체포함) 데이터를 정리한다.
    @list_route()
    def trend(self, request):
        get = request.GET.copy()
        if 'type' in get:
            qs = Rating.objects.filter(type=get['type'], survey__is_virtual=False, candidate__is_active=True)

            if 'agency' in get and get['agency'] != '전체':
                qs = qs.filter(survey__agency__name=get['agency'])

            qs = qs.order_by('survey__published')

            if qs.count() > 0:
                df = read_frame(qs, fieldnames=['survey__agency', 'survey__office', 'survey__published',
                                                'candidate__name', 'candidate__photo',
                                                'candidate__color', 'rate', 'target'])

                df.rename(columns=lambda x: x.replace('candidate__', ''), inplace=True)
                df['survey__published'] = df['survey__published'].apply(lambda x: x.strftime('%y.%m.%d'))
                df['unique'] = df['survey__office'] + '/' + df['survey__agency'] + '/' + df['survey__published']

                df = df.pivot_table(['rate'], index=['target', 'name', 'color', 'photo'],
                                    columns=['survey__published', 'unique'])
                df.columns = df.columns.droplevel(level=0)
                df = df.T
                # df = df.pivot_table(['rate'], index=['survey__published', 'unique', 'target'],
                #                     columns=['name', 'color', 'photo'])

                # 설문조사가 비는 부분은 이전 값으로 채우고 나머지 값들은 0으로 채훈다.
                df = df.fillna(method='ffill').fillna(0)

                categories = list(df.reset_index()['unique'])

                results = df.to_dict('list')

                modified = defaultdict(list)
                for (target, name, color, photo), value in results.items():
                    modified[target].append({
                        'name': name,
                        'color': color,
                        'photo': photo,
                        'data': [x if x != 0 else None for x in value]
                    })

                return Response({'count': len(categories), 'categories': categories, 'results': modified})
            else:
                return Response({'count': 0, 'categories': [], 'results': []})
        else:
            return Response({'status': 'error', 'message': 'There is no product'})

    def filter_queryset(self, queryset):
        request = self.request

        qs = queryset

        if 'type' in request.GET:
            qs = queryset.filter(rating__type=request.GET['type']).distinct()

        if 'virtual' in request.GET:
            qs = qs.filter(is_virtual=request.GET['virtual'])

        return qs.order_by('-published', '-office', '-agency')

    # Override
    def get_serializer_class(self):
        if hasattr(self, 'action'):
            if self.action in self.serializers:
                return self.serializers[self.action]
        return self.serializers['default']

    def perform_create(self, serializer):
        serializer.save()
