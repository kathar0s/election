from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return render(request, 'election/index.html', {'category': 'total'})


def gender(request):
    return render(request, 'election/gender.html', {'category': 'sex'})


def age(request):
    return render(request, 'election/age.html', {'category': 'age'})


def region(request):
    return render(request, 'election/region.html', {'category': 'region'})
