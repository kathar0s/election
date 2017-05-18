from django.db import models


class InitDatabaseLog(models.Model):

    query_id = models.CharField(max_length=100, db_index=True, unique=True, verbose_name=u'업데이트명')
    is_execute = models.BooleanField(default=False, verbose_name=u'실행 여부')
    execute_date = models.DateTimeField(auto_now_add=True, verbose_name=u'실행일')

    def __str__(self):
        return "[%s] %s" % (self.query_id, self.is_execute)

    class Meta:
        verbose_name = '데이터베이스 업데이트 로그'
        verbose_name_plural = '데이터베이스 업데이트 로그 목록'


class Candidate(models.Model):
    number = models.PositiveSmallIntegerField('기호 번호', default=0, blank=True)
    name = models.CharField('이름', max_length=20, default='', db_index=True)
    party = models.CharField('소속당', max_length=20, default='', blank=True)

    is_active = models.BooleanField('출마여부', default=True, blank=True)
    photo = models.CharField('사진', max_length=250, default='')
    color = models.CharField('색상(HEX)', max_length=7, default='#b6bcc7')

    icon = models.ImageField('아이콘', blank=True)

    def __str__(self):
        return "[%s번 %s] %s" % (self.number, self.party, self.name)

    class Meta:
        verbose_name = '후보자'
        verbose_name_plural = '후보자 목록'


# 여론조사기관
class Agency(models.Model):
    name = models.CharField('이름', default='', max_length=40)
    aliases = models.CharField('별칭', max_length=250, default='', help_text='콤마로 구분')

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = '여론조사기관'
        verbose_name_plural = '여론조사기관 목록'


class Office(models.Model):
    name = models.CharField('이름', default='', max_length=40)
    alias = models.CharField('별칭', default='', max_length=40)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = '여론조사 의뢰기관'
        verbose_name_plural = '여론조사 의뢰기관 목록'


class Survey(models.Model):
    SOURCES = [
        ('daum', '다음'),
        ('naver', '네이버')
    ]

    agency = models.ForeignKey(Agency, db_index=True, verbose_name='여론조사기관')
    office = models.CharField('여론조사 의뢰기관', max_length=250, default='')
    published = models.DateField('여론조사 발표일', default=None, null=True)

    name = models.CharField('여론조사명', max_length=80)
    description = models.TextField('여론조사 정보', default='')
    link = models.CharField('링크', max_length=200, default='')

    is_virtual = models.BooleanField('가상여부', default=False)

    source = models.CharField('출처', max_length=10, choices=SOURCES, default='')

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = '여론조사'
        verbose_name_plural = '여론조사 목록'


# 지지율
class Rating(models.Model):
    TYPES = [
        ('total', '종합'),
        ('region', '지역별'),
        ('age', '연령별'),
        ('sex', '성별'),
    ]

    survey = models.ForeignKey(Survey, verbose_name='여론조사')

    type = models.CharField('종류', choices=TYPES, max_length=20, default='total')
    target = models.CharField('대상', db_index=True, max_length=20, default='', help_text='지역명, 연령대, 성별')

    candidate = models.ForeignKey(Candidate, db_index=True, verbose_name='후보')
    rate = models.FloatField('지지율', default=0.0)

    def __str__(self):
        return "[%s/%s] %s: %s" % (self.survey, self.type, self.candidate, self.rate)

    class Meta:
        verbose_name = '지지율'
        verbose_name_plural = '지지율 목록'
