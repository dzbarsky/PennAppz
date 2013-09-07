import json

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render

from database import DatabaseManager
from courseAdvisor.models import Course

@csrf_exempt
def course_search(request):
	if not request.is_ajax():
		print 'not ajax'
		return
	coursecode = request.POST['coursecode']
	db = DatabaseManager()
	courses = db.determine_searched_course(coursecode)
	print courses
	jsonified = json.dumps(courses)
        return HttpResponse(jsonified)

def index(request):
	return render(request, 'courseAdvisor/index.html')
