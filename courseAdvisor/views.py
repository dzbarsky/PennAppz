from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render

from courseAdvisor.models import Course

@csrf_exempt
def course_search(request):
	if request.is_ajax():
            message = request.POST['message'];
        else:
            message = "Not Ajax"
        return HttpResponse(message)

def index(request):
	return render(request, 'courseAdvisor/index.html')
