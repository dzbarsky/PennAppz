import sys
from itertools import *

import requests
import simplejson as json
import MySQLdb
import os
import math

from nemo.models import Course, Instructor, Department, Links

import pprint
import nltk
import string
import re

class DatabaseManager:
    def __init__(self, key=None):
        self.key = key
        self.db = MySQLdb.connect("localhost", "root", "", "PennApps" )

    def generate_random_course(self):
	course = Course.objects.order_by('?')[0]
	coursearr = self.query_to_dicts("""
		SELECT nemo_course.*
		FROM nemo_course
		WHERE nemo_course.id = '%s' ;
		""" % course.id)
	coursecodes = self.query_to_dicts("""
		SELECT nemo_course.*, nemo_coursecodes.code
		FROM nemo_course
		JOIN nemo_coursecodes
		ON nemo_coursecodes.course_id = nemo_course.id
		WHERE nemo_course.id = '%s' ;
		""" % course.id)
	recs = dict()
	for coursea in coursearr:
	    coursea['coursecodes'] = []
	    recs[course.id] = coursea
	for c in coursecodes:
	    recs[course.id]['coursecodes'].append(c['code'])
	recsArray = []
	for rec in recs.iteritems():
	    recsArray.append(rec[1])
	return recsArray

    def thumbs_up(self,curr_course,sugg_course):
        course1 = min(curr_course.id,sugg_course.id)
        course2 = max(curr_course.id,sugg_course.id)
        sql = """UPDATE nemo_links
        SET strength = strength + 1
        WHERE course1_id = '%s' 
	AND course2_id = '%s'
	""" % (course1,course2)
        self.executeQuery(sql)

    def thumbs_down(self,curr_course,sugg_course):
        course1 = min(curr_course.id,sugg_course.id)
        course2 = max(curr_course.id,sugg_course.id)

        sql="""UPDATE nemo_links
        SET strength = strength - 1
        WHERE course1_id = '%s' 
	AND course2_id = '%s'
	""" % (course1,course2)
        self.executeQuery(sql)

    def recommend_courses(self, entered_string):
        course = self.determine_searched_course(entered_string)
        if course is None:
            return None
        course = Course.objects.get(id=course['id'])
        return self.recommendations(course)

    def recommendations(self, course):
        if not course.preSearched:
            self.generate_course_links(course)
            sql="""
#UPDATE nemo_course SET preSearched=True
#WHERE course_id=%s""" % course.id
            self.executeQuery(sql)

	recommendations = self.query_to_dicts("""
		SELECT c1.*, l1.strength
		FROM nemo_course c1
		JOIN nemo_links AS l1
		ON l1.course1_id = c1.id
		WHERE l1.course2_id = %s
		UNION
		SELECT c2.*, l2.strength
		FROM nemo_course c2
		JOIN nemo_links AS l2
		ON l2.course2_id = c2.id
		WHERE l2.course1_id = %s
		ORDER BY strength DESC
		""" % (course.id, course.id))
	ids = []
	recs = dict()
	for rec in recommendations:
	    rec['coursecodes'] = []
            recs[rec['id']] = rec
	    ids.append(str(rec['id']))
	recsString = ','.join(ids)
	coursecodes = self.query_to_dicts("""
		SELECT nemo_course.id, nemo_coursecodes.code 
		FROM nemo_course 
		JOIN nemo_coursecodes 
		ON nemo_coursecodes.course_id = nemo_course.id 
		WHERE nemo_course.id IN (%s) ;
		""" % recsString)
	for c in coursecodes:
	    recs[c['id']]['coursecodes'].append(c['code'])
	recsArray = []
	for rec in recs.iteritems():
	    recsArray.append(rec[1])
	recsArray.sort(key=lambda c: c['strength'], reverse=True)
	return recsArray[1:]

    def find_relevant_courses(self, course):
	
	# Get relevant courses
	dept_courses = self.query_to_dicts("""
	SELECT c2.*, d.code 
	FROM nemo_course c1, 
	   nemo_course c2,
	   nemo_course_departments cd1, 
	   nemo_course_departments cd2, 
	   nemo_department d 
	WHERE c1.id = cd1.course_id 
	AND cd1.department_id = cd2.department_id 
	AND cd2.course_id = c2.id 
	AND d.id = cd1.department_id 
	AND cd1.course_id = %s
	GROUP BY c2.id ;
	""" % course.id)

	instructor_courses = self.query_to_dicts("""
	SELECT c2.*, i.name 
	FROM nemo_course c1, 
	   nemo_course c2,
	   nemo_instructor_courses ic1, 
	   nemo_instructor_courses ic2, 
	   nemo_instructor i 
	WHERE c1.id = ic1.course_id 
	AND ic1.instructor_id = ic2.instructor_id 
	AND ic2.course_id = c2.id 
	AND i.id = ic1.instructor_id 
	AND ic1.course_id = %s
	GROUP BY c2.id ;
	""" % course.id)

	keyword_courses = self.query_to_dicts("""
	SELECT c2.*, k.word
	FROM nemo_course c1, 
	   nemo_course c2,
	   nemo_courses_keywords ck1, 
	   nemo_courses_keywords ck2, 
	   nemo_keyword k 
	WHERE c1.id = ck1.course_id 
	AND ck1.keyword_id = ck2.keyword_id 
	AND ck2.course_id = c2.id 
	AND k.id = ck1.keyword_id 
	AND ck1.course_id = %s ;
	""" % course.id)

	# Build data structure to hold courses
	relevant_courses = dict()
	for dept_course in dept_courses:
	    if not dept_course['id'] in relevant_courses.keys():
                dept_course['same_dept'] = 1
		dept_course['same_instr'] = 0
		dept_course['common_keywords'] = set()
		relevant_courses[dept_course['id']] = dept_course
	for instructor_course in instructor_courses:
	    if not instructor_course['id'] in relevant_courses.keys():
		instructor_course['same_dept'] = 0
                instructor_course['same_instr'] = 1
                instructor_course['common_keywords'] = set()
		relevant_courses[instructor_course['id']] = instructor_course 
	    else:
		relevant_courses[instructor_course['id']]['same_instr'] = 1
	for keyword_course in keyword_courses:
	    if not keyword_course['id'] in relevant_courses:
		keyword_course['same_dept'] = 0
                keyword_course['same_instr'] = 0
                keyword_course['common_keywords'] = set()
		keyword_course['common_keywords'].add(keyword_course['word'])
		relevant_courses[keyword_course['id']] = keyword_course
	    else:
		relevant_courses[keyword_course['id']]['common_keywords'].add(keyword_course['word'])

	return relevant_courses

    def get_course_links(self, course):
	links1  = Links.objects.filter(course1_id__exact=course['id']).values()
	links2  = Links.objects.filter(course2_id__exact=course['id']).values()
	links = []
	for link in links1:
	    links.append(link['id'])
	for link in links2:
	    links.append(link['id'])
	return links

    def generate_course_links(self, entered_course):
        courses = self.find_relevant_courses(entered_course)
        my_course = courses[entered_course.id]

	linked_courses = self.get_course_links(my_course)
	
        # Calculate link weights
        for course_id in courses:
	    if course_id is my_course['id'] or course_id in linked_courses:
	        pass
            course = courses[course_id]
	    link_strength = 0
	    if course['same_dept']:
		link_strength += 8
	    if course['same_instr']:
		if course['same_dept']:
		    link_strength += 10
		else:
		    link_strength += 15
	    link_strength += len(course['common_keywords']) * 4
	    link_strength -= math.fabs(course['difficulty'] - my_course['difficulty']) * 2
	    link_strength += float(course['courseQuality'])
	    link_strength += float(course['instructorQuality'])
	    course1 = min(course['id'], my_course['id']) 
	    course2 = max(course['id'], my_course['id'])
	    link = Links(course1_id=course1, course2_id=course2, strength=link_strength)
	    link.save()

    def determine_searched_course(self,entered_string):
        matches = re.match(r'([a-zA-Z]{3,4})[-| ]?([0-9]{2,3})',entered_string);
        #strip punctuation from remaining string to get course number
        if matches is None:
            return None

        course_number = matches.group(1) + '-' + matches.group(2)

        searched_course = Course.objects.filter(coursecodes__code__exact=course_number)
        if len(searched_course) is 0:
            return None
	return searched_course.values()[0]

    def find_course(self, course_id):
	course = Course.objects.get(id=course_id)
	return course

    def query_to_dicts(self, query_string, *query_args):
	cursor = self.db.cursor()
	cursor.execute(query_string, query_args)
	col_names = [desc[0] for desc in cursor.description]
	while True:
	    row = cursor.fetchone()
	    if row is None:
	        break
	    row_dict = dict(izip(col_names, row))
	    yield row_dict
	return

    def executeQuery(self, sql):
        cursor = self.db.cursor()
        try:
            cursor.execute(sql)
            self.db.commit()
            return cursor.fetchall()
        except Exception as e:
            print "\n~~~~~~~~QUERY FAILED: " + sql
            print e
            self.db.rollback()
            return None

    def create_tags(self, description, title, course_id):
        # Add keywords from the title to the description, weighing them by 3x.
        description = description + " " + title + " " + title + " " + title
        # Strip punctuation
        text = ''.join(ch for ch in description if ch not in string.punctuation)
        text = nltk.word_tokenize(text)
        output_tuple = nltk.pos_tag(text);
        self.find_nouns(output_tuple, course_id)

    def find_nouns(self, output_tuples, course_id):
        occurrences = dict()
        for item in output_tuples:
            if item[1] in ("NN", "NNP", "NNS"):
                prev = 0
                if item[0] in occurrences:
                    prev = occurrences[item[0]]
                occurrences[item[0]] = prev + 1

                # Insert word into database
                sql="""INSERT IGNORE INTO nemo_keyword(word)
VALUES ('%s')""" % item[0]
                self.executeQuery(sql)

        for item in occurrences:
            # Add keyword to the keyword list for the current course
            sql="""INSERT INTO nemo_courses_keywords(course_id, number, keyword_id)
SELECT %s, %s, id FROM nemo_keyword WHERE word='%s'""" % (course_id,
                                                                   occurrences[item],
                                                                   item)
            self.executeQuery(sql)

    # Retrieves an endpoint on the Penn Course Review API
    def get_data(self, endpoint):
        base_url = "http://api.penncoursereview.com/v1"
        url = base_url + endpoint + "?token=" + self.key
        r = requests.get(url)
        if hasattr(r, 'json'):
            return r.json()
        else:
            return json.loads(r.content)

    # Retrieve a list of course reviews for a given department
    def get_courses(self):
        course_ids = []
        departments = self.get_data("/depts")
        #if True:
        #    dept = departments['result']['values'][0]
        for dept in departments['result']['values']:
            courses = self.get_data(dept['path'])
            for course in courses['result']['coursehistories']:
                course_ids.append(course['id'])
        return course_ids

    def populate_database(self, instructors=False):
        def escape(val):
            return val.replace("'", "\\'")

        pp = pprint.PrettyPrinter(indent=4)

        # Populate the course tables
        print "populating courses"
        courses = self.get_courses()
        print "got courses"
        curr = 0
        for course_id in courses:
            if curr % 100 is 0:
                print "Handling course %s of %s\n" % (curr, len(courses))
            curr = curr + 1
            course = self.get_data("/courses/" + str(course_id))

            # Compute the ratings for the course
            reviews = self.get_data(course['result']['coursehistories']['path'] + "/reviews")['result']['values']
            difficulty = 0
            instructorQuality = 0
            courseQuality = 0
            numReviews = 0
            for review in reviews:
                if ('rDifficulty' in review['ratings'] and
                    'rInstructorQuality' in review['ratings'] and
                    'rCourseQuality' in review['ratings']):
                    difficulty += float(review['ratings']['rDifficulty'])
                    instructorQuality += float(review['ratings']['rInstructorQuality'])
                    courseQuality += float(review['ratings']['rCourseQuality'])
                    numReviews = numReviews + 1

            if numReviews is not 0:
                difficulty /= numReviews
                courseQuality /= numReviews
                instructorQuality /= numReviews
            else:
                difficulty = courseQuality = instructorQuality = -1

            # Insert a course into the courses table
            sql = """
INSERT IGNORE INTO nemo_course(id, title, description, preSearched,
difficulty, instructorQuality, courseQuality)
VALUES (%s, '%s', '%s', FALSE, %s, %s, %s)""" % (course_id,
                                                 escape(course['result']['name']),
                                                 escape(course['result']['description']),
                                                 difficulty,
                                                 instructorQuality,
                                                 courseQuality)

            self.executeQuery(sql)

            # Insert the course codes
            for alias in course['result']['aliases']:
                sql = """
INSERT IGNORE INTO nemo_coursecodes(code, course_id)
VALUES ('%s', %s)""" % (alias, course_id)
                self.executeQuery(sql)

            aliases = course['result']['aliases']
            for alias in aliases:
                # Make sure all the departments exist in the database
                dept = alias[0:alias.find('-')]
                sql = """
INSERT IGNORE INTO nemo_department(code)
VALUES ('%s')""" % dept
                self.executeQuery(sql)

                sql = """
INSERT IGNORE INTO nemo_course_departments(course_id, department_id)
SELECT %s, id FROM nemo_department WHERE code='%s'""" % (course_id,
                                                                  dept)

                self.executeQuery(sql)
            self.create_tags(course['result']['description'],
                             course['result']['name'],
                             course_id)

        # Populate the instructor tables.
        for instructor in self.get_data("/instructors")['result']['values']:
            instructor_data = self.get_data(instructor['path'])
        if instructors:
            self.populate_instructors()
        self.db.close()

    def populate_instructors(self):
        def escape(val):
            return val.replace("'", "\\'")
        instructors = self.get_data("/instructors")['result']['values']
        curr = 0
        for instructor in instructors:
            if curr % 100 is 0:
                print "Handling instructors %s of %s\n" % (curr, len(instructors))
            curr = curr + 1
            instructor_data = self.get_data(instructor['path'])

            # Add the instructor the instructor table.
            sql = """
INSERT INTO nemo_instructor(name)
VALUES ('%s')""" % escape(instructor_data['result']['name'])
            self.executeQuery(sql)

            # Add the classes the instructor teaches to the pivot table.
            for review in instructor_data['result']['reviews']['values']:
                for alias in review['section']['aliases']:
                    sql = """
INSERT IGNORE INTO nemo_instructor_courses(instructor_id, course_id)
SELECT instructor.id, coursecodes.course_id
FROM nemo_instructor instructor, nemo_coursecodes coursecodes
WHERE instructor.name = '%s'
AND coursecodes.code = '%s'""" % (escape(instructor_data['result']['name']),
                                  alias[0 : len(alias) - 4])
                self.executeQuery(sql)

        self.db.close()

def main(key):
    db = DatabaseManager(key)
    #db.executeQuery("drop database pennapps;")
    #db.executeQuery("create database pennapps;")
    #os.system("python ../manage.py syncdb")
    #db.executeQuery("use pennapps")
    #db.populate_database()
    db.populate_instructors()

if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print "usage: scores.py <apikey>"
    else:
        main(*sys.argv[1:])
