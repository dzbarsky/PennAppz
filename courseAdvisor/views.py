from django.http import HttpResponse
from django.shortcuts import render

from courseAdvisor.models import Course

def course_search(request):
	return HttpResponse('hi')

def index(request):
	return render(request, 'courseAdvisor/index.html')
