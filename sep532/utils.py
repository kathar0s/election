# -*- coding: utf-8 -*-
import hashlib
import json
import re
import demjson
import sys
from urllib.request import urlopen, quote

from bs4 import BeautifulSoup as Bs
from django.conf import settings
from django.db.models import Q

from election.models import Agency, Survey, Rating, Candidate, Office
from dateutil.parser import parse


def logger(message):
    if settings.DEBUG:
        print(message)


class BaseCrawler(object):
    """Crawler Base object"""

    url = ''
    html = ''
    rating = None
    categories = None

    def __init__(self, url=""):
        self.url = url
        self.rating = dict()
        self.categories = ['종합', '지역별', '연령별', '성별']

        # url이 존재하는 경우에는 html을 먼저 읽어온다.
        if self.url != "":
            self.get_html()

    def get_html(self):
        f = urlopen(self.url)
        self.html = f.read()
        f.close()

    def set_url(self, url):
        self.url = url

    def get_url(self):
        return self.url

    def get_json(self):
        pass


class NaverCrawler(BaseCrawler):

    def __init__(self, *args, **kwargs):
        kwargs['url'] = "http://news.naver.com/main/election/president2017/trend/survey.nhn"
        super(NaverCrawler, self).__init__(*args, **kwargs)

    def get_json(self):

        self.get_html()

        # URL Open 후에 해당 IO는 Close한다.
        soup = Bs(self.html, "html.parser")
        # xpath, select, 여러가지 방법으로 select를 할 수 있음

        script = soup.select('#wrap > div > script')

        categories = ['후보정보', '종합', '가상 N자', '정당지지율', '지역별', '연령별', '성별']

        # 후보정보를 먼저 작업한다.
        string = script[categories.index('후보정보')].text.split('CANDIDATE_INFO = ')
        data = string[1].split(';')[0]

        self.rating['후보정보'] = demjson.decode(data)

        for category in self.categories:
            string = script[categories.index(category)].text.split('jindo.$A(')
            data = string[1].split(');')[0]

            # json으로 변환하는 과정에서 오류나는 function은 삭제한다.
            data = re.sub('istoday\(.*\),', '\"N\",', data)

            # javascript data object to json data object
            json_data = demjson.decode(data)

            self.rating[category] = json_data['data'] if 'data' in json_data else json_data

        return self.rating


class DaumCrawler(BaseCrawler):

    def __init__(self, *args, **kwargs):
        # 지역별, 종합, 연령별, 성별
        super(DaumCrawler, self).__init__(*args, **kwargs)

    def get_json(self):

        # 다음에서는 Ajax통신을 통해 데이터를 가져오므로 카테고리별로 JSON을 가져온다.
        base_url = "http://comment.daum.net/poll/polls/tags/of/all/%s,%s?limit=1000"

        for category in self.categories:
            self.set_url(base_url % (quote('지지율'), quote(category)))
            self.get_html()

            json_data = json.loads(self.html.decode('utf-8'))

            self.rating[category] = json_data['data'] if 'data' in json_data else json_data

        return self.rating


class Parser(object):
    crawler = None
    crawl_data = None

    def __init__(self, crawler):
        self.crawler = crawler
        self.crawl_data = self.crawler.get_json()

    @staticmethod
    def get_agency(data):
        pass

    @staticmethod
    def get_offices(data):
        pass

    @staticmethod
    def get_published(data):
        pass

    @staticmethod
    def get_description(data):
        pass

    @staticmethod
    def get_link(data):
        pass

    @staticmethod
    def get_target(data):
        pass

    @staticmethod
    def get_rates(data):
        pass

    def get_moons_rate(self, data):
        pass

    @staticmethod
    def get_unique(rate, agency, published):
        return hashlib.md5('{}/{}/{}'.format(agency.name,
                                             published.strftime('%y.%m.%d'),
                                             rate).encode('utf-8')).hexdigest()

    @staticmethod
    def validation(data):
        pass

    @staticmethod
    def get_source():
        pass

    def parse_rates(self, data, survey):
        pass

    def parse_save(self):

        for category in self.crawl_data.keys():
            logger('\n{} 설문조사 정보를 알아보고 있습니다...'.format(category))
            for result in reversed(self.crawl_data[category]):

                # data가 있는 경우에는 data를 변경
                result = result['data'] if 'data' in result else result

                # 1. 설문조사 기관명을 가져온다.
                agency_name = self.get_agency(result)

                # 기존에 있는 기관인지 확인해보고 설문조사 기관을 가져온다. (없으면 새로 생성)
                try:
                    agency = Agency.objects.get(Q(name__icontains=agency_name) | Q(aliases__icontains=agency_name))
                except Agency.DoesNotExist:
                    agency = Agency.objects.create(name=agency_name)
                except Agency.MultipleObjectsReturned:
                    logger('[오류] 설문조사 기관이 2개 이상 검색되었습니다!')
                    sys.exit(0)

                offices = self.get_offices(result)
                for i, office_name in enumerate(offices):
                    try:
                        office = Office.objects.get(Q(name__exact=office_name) | Q(alias__icontains=office_name))
                    except Office.DoesNotExist:
                        office = Office.objects.create(name=office_name)
                    except Office.MultipleObjectsReturned:
                        logger('[오류] 설문조사의뢰기관이 2개 이상 검색되었습니다!')
                        sys.exit(0)
                    offices[i] = office.name

                # 의뢰기관명을 정렬한다.
                offices.sort()

                # 2. 설문조사가 기존에 있는 내용인지, 새로 만들어야하는지 확인한다.
                published = self.get_published(result)
                survey_name = '/'.join(['-'.join(offices), agency.name])
                survey_name = '[{}] {} 여론조사'.format(survey_name, published.strftime('%y.%m.%d'))
                description = self.get_description(result)

                is_virtual = True if description.startswith('가상') or description.startswith('[가상') else False

                defaults = {
                    'name': survey_name,
                    'description': description,
                    'source': self.get_source(),
                    'link': self.get_link(result)
                }

                # 설문조사기관과 설문조사 발행일에 대하여 같은 내용이 있으면 Update를 하고
                # 없는 경우에는 Create를 한다.
                # 설문조사기관과 발행일이 같아도 의뢰기관이 다른 경우에 대해서도 설문조사가 또 이루어지므로
                # 의뢰기관도 고려해야한다.
                # 의뢰기관명이 Naver와 Daum이 통일되지 않는 경우가 많으므로..
                # 설문조사 결과가 다른 경우에는 새로운 설문조사라고 판단한다.
                # 설문조사 결과가 다른 지는 문재인 후보의 지지율을 보고 판단한다. (unique를 md5로 고유화)

                survey, is_created = Survey.objects.update_or_create(agency=agency,
                                                                     office='-'.join(offices),
                                                                     is_virtual=is_virtual,
                                                                     published=published.strftime('%Y-%m-%d'),
                                                                     defaults=defaults)
                if is_created:
                    logger('{}가 생성되었습니다.'.format(survey_name))

                # 이번 설문이 어떤 종류인지 파악한다 (지역, 성별, 종합, 연령)
                rating_types = dict(Rating.TYPES)
                type_index = list(rating_types.values()).index(category)
                survey.type = list(rating_types.keys())[type_index]

                self.parse_rates(result, survey)


class DaumParser(Parser):

    def __init__(self, *args, **kwargs):
        kwargs['crawler'] = DaumCrawler()
        super(DaumParser, self).__init__(*args, **kwargs)

    @staticmethod
    def get_source():
        return 'daum'

    @staticmethod
    def get_offices(data):
        offices = data['description'].replace('&#8203;', '').split('/')[0]
        offices = offices.split('-')
        return list(map(str.strip, offices))

    @staticmethod
    def get_agency(data):
        return data['description'].split('/')[1].strip()

    @staticmethod
    def get_published(data):
        return parse(data['startTime'])

    @staticmethod
    def get_description(data):
        description = '/'.join(data['description'].split('/')[3:])
        return re.sub('<[^>]*>|[\[\]]|&#8203;', '', description).strip()

    @staticmethod
    def get_link(data):
        return data['extraInfo']

    def get_moons_rate(self, data):
        for option in data['options']:
            if option['title'] == '문재인':
                return option['rate']
        return None

    def parse_rates(self, data, survey):
        logger('{}에 대한 {} 지지율결과를 알아보고 있습니다.'.format(survey.name, data['title']))

        # 해당 설문조사에서 나온 지지율 결과를 저장한다.

        targets = data['title'].split('/')
        for target in targets:
            # 후보자별 지지율을 찾아서 업데이트한다.
            for option in data['options']:

                # 후보자를 찾거나 생성한다.
                candidate, is_created = Candidate.objects.get_or_create(name=option['title'])
                defaults = {
                    'rate': option['rate'],
                }
                if is_created:
                    logger('{} 후보자 정보가 생성되었습니다.'.format(candidate.name))

                if survey.type == 'total' and target != '전국':
                    target = '전국'

                rating, is_created = Rating.objects.update_or_create(
                    candidate=candidate, target=target, type=survey.type, survey=survey, defaults=defaults)
                if is_created:
                    logger('{} 후보자의 {} 지지율 {}%가 등록되었습니다.'.format(candidate.name, target,
                                                                 option['rate']))


class NaverParser(Parser):

    def __init__(self, *args, **kwargs):
        kwargs['crawler'] = NaverCrawler()
        self.candidate_info = None

        super(NaverParser, self).__init__(*args, **kwargs)

    @staticmethod
    def get_source():
        return 'naver'

    @staticmethod
    def get_offices(data):
        list_offices = data['surveyAgency'].replace('&#8203;', '')
        offices = list_offices.split('·')[:-1]
        if len(offices) == 0:
            offices.append(list_offices)
        return list(map(str.strip, offices))

    @staticmethod
    def get_agency(data):
        return data['surveyAgency'].split('·')[-1].strip()

    @staticmethod
    def get_published(data):
        return parse(data['formatDate'])

    @staticmethod
    def get_description(data):
        return re.sub('<[^>]*>|[\[\]]|&#8203;', '', data['info']).strip()

    @staticmethod
    def get_link(data):
        return data['linkUrl']

    def get_moons_rate(self, data):
        categories = data['category'] if 'category' in data else [data]
        for category in categories:
            for option in category['candidateList']:
                if self.candidate_info[option['id']]['name'] == '문재인':
                    return option['rating']
        return None

    def parse_save(self, *args, **kwargs):
        self.candidate_info = self.crawl_data['후보정보']
        del self.crawl_data['후보정보']
        for candidate in self.candidate_info.values():
            try:
                obj = Candidate.objects.get(name=candidate['name'])
                obj.party = candidate['partyName'].replace('민주당', '더불어민주당')
                obj.color = candidate['colorCode']
                obj.photo = candidate['largePhoto']
                obj.save()
            except Candidate.DoesNotExist:
                pass

        super(NaverParser, self).parse_save(*args, **kwargs)

    def parse_rates(self, data, survey):
        categories = data['category'] if 'category' in data else [data]
        for category in categories:

            if 'name' not in category:
                category['name'] = '전국'
            targets = category['name'].split('/')

            logger('{}에 대한 {} 지지율결과를 알아보고 있습니다.'.format(survey.name, category['name']))

            for target in targets:
                target = re.sub('<[^>]*>|\s', '', target)

                # 연령대별로 구분되는 경우에는 한번더 정제할 필요가 있음
                if survey.type == 'age':
                    tmp = re.findall(r'\d+', target)[0]
                    tmp = round(int(tmp) / 10) * 10

                    # 60대 결과의 경우에는 이상으로 구분하여 표시
                    if tmp == 60:
                        target = '{}세이상'.format(tmp)
                    else:
                        target = '{}대'.format(tmp)

                # 후보자별 지지율을 찾아서 업데이트한다.
                for option in category['candidateList']:

                    if option['id']:
                        # 후보자를 찾거나 생성한다.
                        candidate_name = self.candidate_info[option['id']]['name']
                        candidate, is_created = Candidate.objects.get_or_create(name=candidate_name)
                        rate = 0 if option['rating'] == '' else option['rating']
                        defaults = {
                            'rate': rate,
                        }
                        if is_created:
                            logger('{} 후보자 정보가 생성되었습니다.'.format(candidate.name))

                        if survey.type == 'total' and target != '전국':
                            target = '전국'

                        rating, is_created = Rating.objects.update_or_create(
                            candidate=candidate, target=target, type=survey.type, survey=survey, defaults=defaults)
                        if is_created:
                            logger('{} 후보자의 {} 지지율 {}%가 등록되었습니다.'.format(candidate.name, target, rate))
