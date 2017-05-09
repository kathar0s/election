# -*- coding: utf-8 -*-
from django.apps import apps
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from election.models import InitDatabaseLog, Agency, Office

get_model = apps.get_model


class Command(BaseCommand):
    args = '<no_arguments ...>'
    help = 'Init Database for new environment'

    def handle(self, *args, **options):
        init_db(self, "default_user_init")
        init_db(self, "default_agency_init")
        init_db(self, "default_office_init", True)

        self.stdout.write('Successfully Init Database')


@transaction.atomic
def default_office_init():
    offices = [
        {'name': 'CBS', 'alias': ''},
        {'name': 'EBS', 'alias': ''},
        {'name': 'JTBC', 'alias': ''},
        {'name': 'KBS', 'alias': ''},
        {'name': 'MBC', 'alias': ''},
        {'name': 'MBN', 'alias': ''},
        {'name': 'SBS', 'alias': ''},
        {'name': 'TV조선', 'alias': ''},
        {'name': 'YTN', 'alias': ''},
        {'name': '데일리안', 'alias': ''},
        {'name': '동아일보', 'alias': '동아'},
        {'name': '매일경제', 'alias': '매경'},
        {'name': '문화일보', 'alias': ''},
        {'name': '미디어오늘', 'alias': ''},
        {'name': '서울경제', 'alias': ''},
        {'name': '서울신문', 'alias': '서울'},
        {'name': '세계일보', 'alias': ''},
        {'name': '시사인', 'alias': '시사IN'},
        {'name': '아시아경제', 'alias': ''},
        {'name': '연합뉴스', 'alias': ''},
        {'name': '이데일리', 'alias': ''},
        {'name': '전국 지방대표 7개 언론사', 'alias': ''},
        {'name': '조선일보', 'alias': ''},
        {'name': '중앙일보', 'alias': ''},
        {'name': '채널A', 'alias': ''},
        {'name': '코리아타임즈', 'alias': '코리아타임스'},
        {'name': '프레시안', 'alias': ''},
        {'name': '한겨레신문', 'alias': '한겨레'},
        {'name': '한국갤럽', 'alias': ''},
        {'name': '한국경제신문', 'alias': '한경,한국경제'},
        {'name': '한국일보', 'alias': ''},
        {'name': '한국지방신문협회', 'alias': ''},
    ]

    for office in offices:
        obj, is_created = Office.objects.get_or_create(name=office['name'], alias=office['alias'])
        if is_created:
            print('{} 설문조사의뢰기관이 등록되었습니다.'.format(office['name']))


@transaction.atomic
def default_agency_init():
    agencies = [
        {'aliases': '', 'name': '리얼미터'},
        {'aliases': '', 'name': '알앤써치'},
        {'aliases': '', 'name': '한국리서치'},
        {'aliases': '', 'name': '중앙일보 조사연구팀'},
        {'aliases': '', 'name': '엠브레인'},
        {'aliases': '', 'name': '리서치뷰'},
        {'aliases': '', 'name': '에스티아이'},
        {'aliases': '', 'name': '코리아리서치센터'},
        {'aliases': '', 'name': '리서치플러스'},
        {'aliases': '한국갤럽조사연구소', 'name': '한국갤럽'},
        {'aliases': '리서앤리서치', 'name': '리서치앤리서치'},
        {'aliases': '메트릭스코퍼레이션,매트릭스', 'name': '메트릭스'},
        {'aliases': '칸타퍼블릭', 'name': '칸타코리아'},
        {'aliases': '', 'name': '한겨레경제사회연구원&엠알시케이(MRCK)'}
    ]

    for agency in agencies:
        obj, is_created = Agency.objects.get_or_create(name=agency['name'], aliases=agency['aliases'])
        if is_created:
            print('{} 설문조사기관이 등록되었습니다.'.format(agency['name']))


@transaction.atomic
def default_user_init():
    try:
        User.objects.get(username='admin')
    except User.DoesNotExist:
        # admin superuser 계정 생성
        User.objects.create_superuser('admin', 'kathar0s.dev@gmail.com', 'sep532sep532')


def reinit_db(method_name):
    # 실행여부에 관계없이 다시 실행한다.
    eval(method_name + "()")
    executed(method_name)


def init_db(self, method_name, force=False):
    if not is_execute(method_name) or force:
        eval(method_name + "()")
        executed(method_name)
        self.stdout.write('Execute %s db init OK' % method_name)


def executed(query_id):
    try:
        log = InitDatabaseLog.objects.get(query_id=query_id)
        log.is_execute = True
    except InitDatabaseLog.DoesNotExist:
        log = InitDatabaseLog()
        log.query_id = query_id
        log.is_execute = True

    log.save()


def is_execute(query_id):
    try:
        init_log = InitDatabaseLog.objects.get(query_id=query_id)
        return init_log.is_execute
    except InitDatabaseLog.DoesNotExist:
        return False
