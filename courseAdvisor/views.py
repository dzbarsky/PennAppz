from django.http import HttpResponse
from django.shortcuts import render

from courseAdvisor.models import Course

def course_search(request):
		if request.is_ajax():
			message = request.POST
		else:
			message = 'nope'
		return HttpResponse(message)

def index(request):
		return render(request, 'courseAdvisor/index.html')
