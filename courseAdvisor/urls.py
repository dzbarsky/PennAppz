from django.conf.urls import patterns, url

from courseAdvisor import views

urlpatterns = patterns('',

	url(r'^$', views.index, name='index'),
	url(r'^course_search/$', views.course_search, name='course_search'),

)
