from django.conf.urls import patterns, url

from nemo import views

urlpatterns = patterns('',

    url(r'^$', views.index, name='index'),
    url(r'^course_search/$', views.course_search, name='course_search'),
    url(r'^random_course/$', views.random_course, name='random_course'),
    url(r'^user_feedback/$', views.user_feedback, name='user_feedback'),
	

)
