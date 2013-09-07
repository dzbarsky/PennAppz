from django.db import models

# Create your models here.

class Department(models.Model):
	code=models.CharField(max_length=5,unique=True)
	def __unicode__(self):
		return name

class Course(models.Model):
	courseCodes=models.CharField(max_length=1500,null=True)
	title=models.CharField(max_length=200)
	description=models.CharField(max_length=1500,null=True)
	keywords=models.ManyToManyField(
		'Keyword',
		through='Courses_Keywords',
		symmetrical=False,
	)
	departments=models.ManyToManyField('Department')
	linkedCourses=models.ManyToManyField(
		'self',
		through='Links',
		symmetrical=False,
		related_name='linkedCourse+',
	)
	def __unicode__(self):
		return title

class Keyword(models.Model):
	word=models.CharField(max_length=30,unique=True)
	def __unicode__(self):
		return word

class Links(models.Model):
	course1=models.ForeignKey('Course', related_name='course1s')
	course2=models.ForeignKey('Course', related_name='course2s')
	strength=models.IntegerField()

class Courses_Keywords(models.Model):
	course_id=models.ForeignKey('Course')
	keyword_id=models.ForeignKey('Keyword')
	number=models.IntegerField()
