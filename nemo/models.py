from django.db import models

# Create your models here.

class Department(models.Model):
    code=models.CharField(max_length=5,unique=True)

class Course(models.Model):
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
    preSearched=models.BooleanField()
    difficulty=models.DecimalField(max_digits=5, decimal_places=2)
    courseQuality=models.DecimalField(max_digits=5, decimal_places=2)
    instructorQuality=models.DecimalField(max_digits=5, decimal_places=2)

class CourseCodes(models.Model):
    code=models.CharField(max_length=10, unique=True)
    course=models.ForeignKey('Course')

class Keyword(models.Model):
	word=models.CharField(max_length=50,unique=True)

class Links(models.Model):
	course1=models.ForeignKey('Course', related_name='course1s')
	course2=models.ForeignKey('Course', related_name='course2s')
	strength=models.IntegerField()

class Courses_Keywords(models.Model):
	course=models.ForeignKey('Course')
	keyword=models.ForeignKey('Keyword')
	number=models.IntegerField()

class Instructor(models.Model):
    name=models.CharField(max_length=100, unique=True)
    courses=models.ManyToManyField('Course')

