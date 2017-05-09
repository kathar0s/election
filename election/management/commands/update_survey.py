# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from election.models import Candidate
from sep532.utils import DaumParser, NaverParser


class Command(BaseCommand):
    args = '<date ...>'
    help = 'Update survey data'

    def handle(self, *args, **options):

        # DAUM과 NAVER에서 설문조사 결과를 가져온다.
        print('DAUM 여론조사 정보를 가져옵니다.')
        parser = DaumParser()
        parser.parse_save()

        print('NAVER 여론조사 정보를 가져옵니다.')
        parser = NaverParser()
        parser.parse_save()

        self.calibrate_candidate()

    @staticmethod
    def calibrate_candidate():
        candidates = [
            {
                'name': '문재인',
                'party': '더불어민주당'
            }, {
                'name': '홍준표',
                'party': '자유한국당'
            }, {
                'name': '안철수',
                'party': '국민의당'
            }, {
                'name': '유승민',
                'party': '바른정당'
            }, {
                'name': '심상정',
                'party': '정의당'
            }, {
                'name': '조원진',
                'party': '새누리당'
            }, {
                'name': '오영국',
                'party': '경제애국당'
            }, {
                'name': '장성민',
                'party': '국민대통합당'
            }, {
                'name': '이재오',
                'party': '늘푸른한국당'
            }, {
                'name': '김선동',
                'party': '민중연합당'
            }, {
                'name': '남재준',
                'party': '통일한국당',
                'is_active': False
            }, {
                'name': '이경희',
                'party': '한국국민당'
            }, {
                'name': '김정선',
                'party': '한반도미래연합',
                'is_active': False
            }, {
                'name': '윤홍식',
                'party': '홍익당'
            }, {
                'name': '김민찬',
                'party': '무소속'
            }, {
                'name': '이재오',
                'party': '정의당'
            },
        ]

        Candidate.objects.all().update(is_active=False)
        for number, candidate in enumerate(candidates):
            name = candidate['name']
            del candidate['name']
            candidate['number'] = number + 1
            candidate['is_active'] = candidate['is_active'] if 'is_cative' in candidate else True
            Candidate.objects.update_or_create(name=name, defaults=candidate)
