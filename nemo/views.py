import json
import decimal

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render

from database import DatabaseManager
from nemo.models import Course

def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

def course_search(request):
    if not request.is_ajax():
        print 'not ajax'
        return
    coursecode = request.POST['coursecode']
    db = DatabaseManager()
    courses = db.recommend_courses(coursecode)
    jsonified = json.dumps(courses, default=decimal_default)
    return HttpResponse(jsonified)

def index(request):
    return render(request, 'nemo/index.html')

def random_course(request):
    if not request.is_ajax():
	print 'not ajax'
	return
    db = DatabaseManager()
    course = db.generate_random_course()
    jsonified = json.dumps(course, default=decimal_default)
    return HttpResponse(jsonified) 

def user_feedback(request):
    if not request.is_ajax():
	print 'not ajax'
	return
    db = DatabaseManager()
    coursecode1 = request.POST['searched_course']
    courseobj1 = db.determine_searched_course(coursecode1)
    course1 = db.find_course(courseobj1['id'])
    courseid2 = request.POST['courseid2']
    course2 = db.find_course(courseid2)
    feedback = request.POST['feedback']
    print course1
    print course2
    print feedback
    if feedback == 'thumbs_up':
	db.thumbs_up(course1, course2)
    else:
	db.thumbs_down(course1, course2)
    return HttpResponse()
