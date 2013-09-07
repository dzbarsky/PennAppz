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
                print e
                db.rollback()

        db = MySQLdb.connect("localhost", "root", "", "PennApps" )

        pp = pprint.PrettyPrinter(indent=4)

        for course_id in self.get_courses():
            course = self.get_data("/courses/" + str(course_id))
            pp.pprint(course)

            # Insert a course into the courses table
            sql = """INSERT INTO courseAdvisor_course(course_id, title, description)
VALUES (%s, '%s', \"%s\")""" % (course_id,
                              course['result']['name'],
                              course['result']['description'])
            execute(sql, db)

            aliases = course['result']['aliases']
            for alias in aliases:
                dept = alias[0:alias.find('-')]
                print dept
                sql = """INSERT IGNORE INTO courseAdvisor_department(name)
VALUES ('%s')""" % dept
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
