import sys

import requests
import simplejson as json
import MySQLdb

import pprint

class DatabasePopulater:
    def __init__(self, key):
        self.key = key

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

    def populate_database(self):

        def execute(sql, db):
            cursor = db.cursor()
            try:
                cursor.execute(sql)
                db.commit()
            except Exception as e:
                print "\n~~~~~~~~FAILED: " + sql
                print e
                db.rollback()

        db = MySQLdb.connect("localhost", "root", "", "PennApps" )

        pp = pprint.PrettyPrinter(indent=4)

        for course_id in self.get_courses():
            course = self.get_data("/courses/" + str(course_id))
            #pp.pprint(course)

            #print json.dumps(course['result']['aliases']),
            # Insert a course into the courses table
            sql = """INSERT INTO courseAdvisor_course(id, courseCodes, title, description)
VALUES (%s, '%s', '%s', \"%s\")""" % (course_id,
                                     json.dumps(course['result']['aliases']),
                                     course['result']['name'],
                                     course['result']['description'])
            execute(sql, db)

            aliases = course['result']['aliases']
            for alias in aliases:
                # Make sure all the departments exist in the database
                dept = alias[0:alias.find('-')]
                sql = """INSERT IGNORE INTO courseAdvisor_department(code)
VALUES ('%s')""" % dept
                execute(sql, db)

                sql = """INSERT INTO courseAdvisor_course_departments(course_id, department_id)
SELECT %s, id FROM courseAdvisor_department WHERE code='%s'""" % (course_id,
                                                                  dept)

                #print sql
                execute(sql, db)

        db.close()

def main(key):
    dp = DatabasePopulater(key)
    dp.populate_database()

if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print "usage: scores.py <apikey>"
    else:
        main(*sys.argv[1:])
