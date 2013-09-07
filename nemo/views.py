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
    courses = db.determine_searched_course(coursecode)
    json_courses = []
    print courses
    for course in courses:
        json_course = dict()
        json_course['title'] = course.title
        json_course['description'] = course.description
        json_course['difficulty'] = course.difficulty
        json_course['courseQuality'] = course.courseQuality
        json_course['instructorQuality'] = course.instructorQuality
        json_courses.append(json_course)

    jsonified = json.dumps(json_courses, default=decimal_default)
    return HttpResponse(jsonified)

def index(request):
    return render(request, 'nemo/index.html')
