# -*- coding: utf-8 -*-
from rest_framework import serializers
from election.models import Rating, Survey, Agency
from django_pandas.io import read_frame
from collections import defaultdict, OrderedDict


class RatingSerializer(serializers.ModelSerializer):

    candidate = serializers.SerializerMethodField(read_only=True)

    def get_candidate(self, obj):
        return {
            'name': obj.candidate.name,
            'number': obj.candidate.number,
            'party': obj.candidate.party,
            'color': obj.candidate.color,
            'photo': obj.candidate.photo
        }

    class Meta:
        model = Rating
        fields = ('type', 'target', 'candidate', 'rate')


class SurveySerializer(serializers.ModelSerializer):

    agency = serializers.SerializerMethodField(read_only=True)
    results = serializers.SerializerMethodField(read_only=True)

    def get_agency(self, obj):
        return obj.agency.name

    def get_results(self, obj):
        request = self.context['request']
        get = request.GET
        qs = obj.rating_set.exclude(candidate__party='').order_by('-rate')
        if 'type' in get:
            qs = qs.filter(type=get['type'])

        # 지역별 1위한 후보의 기호번호를 가져온다.
        df = read_frame(qs, fieldnames=['target',
                                        'candidate__name', 'candidate__number', 'candidate__party', 'rate',
                                        'candidate__color', 'candidate__photo'])

        df.rename(columns=lambda x: x.replace('candidate__', ''), inplace=True)

        dict_data = df.set_index(['target', 'name']).T.to_dict()
        dict_data = OrderedDict(sorted(dict_data.items(), key=lambda x: x[1]['rate'], reverse=True))

        # target별로 지지율 1위인 기호번호를 가져온다.
        df = df.pivot_table(['rate'], index=['target'], columns=['number'], fill_value=0)

        df.columns = df.columns.droplevel(level=0)
        df['top'] = df.idxmax(axis=1)
        df.reset_index(inplace=True)
        df.set_index('target', inplace=True)

        # 지역별 1위 후보 dict 정보
        top = df['top'].to_dict()

        result = defaultdict(dict)
        for key, candidate in dict_data.items():
            region, name = key
            candidate['name'] = name
            if 'candidates' in result[region]:
                result[region]['candidates'].append(candidate)
            else:
                result[region]['target'] = region
                result[region]['candidates'] = [candidate]
            result[region]['top'] = top[region]

        return result

    class Meta:
        model = Survey
        fields = ('agency', 'office', 'published', 'name', 'results', 'description', 'link', 'is_virtual', 'source')


class AgencySerializer(serializers.ModelSerializer):

    class Meta:
        model = Agency
        fields = ('name', 'aliases')
