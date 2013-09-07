import sys

import requests
import simplejson as json
import MySQLdb

import os

import pprint
import nltk
import string
import re

class DatabaseManager:
    def __init__(self, key=None):
        self.key = key
        self.db = MySQLdb.connect("localhost", "root", "", "PennApps" )

    def determine_searched_course(self,entered_string):
	matches = re.match(r'([a-zA-Z]{3,4})[-| ]?([0-9]{2,3})',entered_string);
        #strip punctuation from remaining string to get course number
	course_number = matches.group(1) + '-' + matches.group(2)

        sql="""SELECT courses.*
               FROM courseAdvisor_course courses, courseAdvisor_coursecodes cc
               WHERE cc.code = '%s'
               AND cc.course_id = courses.id""" % (course_number)
        searched_course = self.executeQuery(sql)
        return searched_course

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
                sql="""INSERT IGNORE INTO courseAdvisor_keyword(word)
VALUES ('%s')""" % item[0]
                self.executeQuery(sql)

        for item in occurrences:
            # Add keyword to the keyword list for the current course
            sql="""INSERT INTO courseAdvisor_courses_keywords(course_id, number, keyword_id)
SELECT %s, %s, id FROM courseAdvisor_keyword WHERE word='%s'""" % (course_id,
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
        if True:
            dept = departments['result']['values'][0]
        #for dept in departments['result']['values']:
            courses = self.get_data(dept['path'])
            for course in courses['result']['coursehistories']:
                course_ids.append(course['id'])
        return course_ids

    def populate_database(self, instructors=False):
        def escape(val):
            return val.replace("'", "\\'")

        pp = pprint.PrettyPrinter(indent=4)

        # Populate the course tables
        for course_id in self.get_courses():
            course = self.get_data("/courses/" + str(course_id))

            # Insert a course into the courses table
            sql = """
INSERT INTO courseAdvisor_course(id, title, description, preSearched)
VALUES (%s, '%s', '%s', FALSE)""" % (course_id,
                                     escape(course['result']['name']),
                                     escape(course['result']['description']))
            self.executeQuery(sql)

            # Insert the course codes
            for alias in course['result']['aliases']:
                sql = """
INSERT INTO courseAdvisor_coursecodes(code, course_id)
VALUES ('%s', %s)""" % (alias, course_id)
                self.executeQuery(sql)

            aliases = course['result']['aliases']
            for alias in aliases:
                # Make sure all the departments exist in the database
                dept = alias[0:alias.find('-')]
                sql = """
INSERT IGNORE INTO courseAdvisor_department(code)
VALUES ('%s')""" % dept
                self.executeQuery(sql)

                sql = """
INSERT IGNORE INTO courseAdvisor_course_departments(course_id, department_id)
SELECT %s, id FROM courseAdvisor_department WHERE code='%s'""" % (course_id,
                                                                  dept)

                self.executeQuery(sql)
            self.create_tags(course['result']['description'],
                             course['result']['title'],
                             course_id)

        self.db.close()
        # Populate the instructor tables.
'''
        for instructor in self.get_data("/instructors")['result']['values']:
            instructor_data = self.get_data(instructor['path'])
        if instructors:
            for instructor in self.get_data("/instructors")['result']['values']:
                instructor_data = self.get_data(instructor['path'])

                # Add the instructor the instructor table.
                sql = """
INSERT INTO courseAdvisor_instructor(name)
VALUES ('%s')""" % instructor_data['result']['name']
                self.executeQuery(sql)

                # Add the classes the instructor teaches to the pivot table.
                for review in instructor_data['result']['reviews']['values']:
                    for alias in review['section']['aliases']:
                        sql = """
INSERT IGNORE INTO courseAdvisor_instructor_courses(instructor_id, course_id)
SELECT instructor.id, coursecodes.course_id
FROM courseAdvisor_instructor instructor, courseAdvisor_coursecodes coursecodes
WHERE instructor.name = '%s'
AND coursecodes.code = '%s'""" % (instructor_data['result']['name'],
                                  alias[0 : len(alias) - 4])
                    self.executeQuery(sql)
'''


def main(key):
    db = DatabaseManager(key)
    db.executeQuery("drop database pennapps;")
    db.executeQuery("create database pennapps;")
    os.system("python ../manage.py syncdb")
    db.executeQuery("use pennapps")
    db.populate_database()

if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print "usage: scores.py <apikey>"
    else:
        main(*sys.argv[1:])
